#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MARSWALK 격자 전처리 — DEM(GeoTIFF) → grid.geojson
"그림(래스터)"을 "칸별 숫자표"로. 앱은 이 geojson을 읽어 칸을 색칠.

칸마다:
  slope_deg : 경사(도)           — DEM 실데이터
  comm      : clear/shadow       — 기지 가시선(지형 기반 추정)
  S1..S5    : 생명점수 지표 0~4   — CRISM/지질 래스터 준 것만, 없으면 null(가짜 안채움)
  score     : 0~100 (ROC 가중합)  — Sᵢ 다 있을 때만

좌표계: 위경도 DEM / 미터 투영 DEM 둘 다 처리(출력은 lon/lat, Leaflet 호환).

실행:
  pip install rasterio numpy
  python build_grid.py --dem jezero_dem.tif --out grid.geojson --cell-px 25
  # 느리면 --cell-px 를 더 키우세요(칸 커지고 빨라짐). 처음엔 25 권장.
"""
import argparse, json, math, sys

MARS_R = 3396190.0  # 화성 반지름 m (USGS 기준)

# ── CRISM 분류(categorical) 맵 RGB → S1(0~4) 룩업 ──────────────────────────
# 출처: Zenodo 5575824 "Jezero crater mineral map"(Parente/Itoh/Saranathan)
#   Jezero_readme.pdf 범례. 각 광물은 High/Medium 신뢰도 2색 → 둘 다 같은 광물로.
# 점수 기준(iMOST 생명흔적 보존광물 우선순위):
#   탄산염·점토·함수실리카 = 4 / 올리빈·점토 혼합(기타 수화) = 3 / 올리빈·휘석(현무암질) = 1
#   미식별(black 0,0,0) · 배경(white 255,255,255) = null
CRISM_PROTOTYPES = [  # (R, G, B, 광물, S1)
    (255,   0,   0, "Olivine",           1),  # Red    (High)
    (153,   0,   0, "Olivine",           1),  #        (Med)
    (  0, 255,   0, "Mg-Carbonate",      4),  # Green  탄산염
    (  0, 153,   0, "Mg-Carbonate",      4),
    (  0, 255, 255, "Fe/Mg-Smectite",    4),  # Cyan   점토(스멕타이트)
    (  0, 153, 153, "Fe/Mg-Smectite",    4),
    (255, 128, 114, "Olivine+Smectite",  3),  # Salmon 올리빈+점토 혼합
    (153,  77,  68, "Olivine+Smectite",  3),
    (128, 128,   0, "Olv.Smect+2.2um",   3),  # Olive  올리빈+점토+Al-OH 혼합
    ( 77,  77,   0, "Olv.Smect+2.2um",   3),
    (255, 215,   0, "Carb.+2.2um",       4),  # Gold   탄산염+Al-OH(점토/실리카)
    (153, 129,   0, "Carb.+2.2um",       4),
    (255, 128,   0, "High-Ca Pyroxene",  1),  # Orange 휘석(현무암질)
    (153,  77,   0, "High-Ca Pyroxene",  1),
    (218, 165,  32, "Low-Ca Pyroxene",   1),  # GoldenRod 휘석
    (130,  99,  19, "Low-Ca Pyroxene",   1),
    (139,  69,  19, "Kaolinite",         4),  # Brown  카올리나이트(점토)
    ( 83,  41,  11, "Kaolinite",         4),
    (  0,   0, 255, "Mg-Smectite 2",     4),  # Blue   점토(스멕타이트)
    (  0,   0, 153, "Mg-Smectite 2",     4),
]
CRISM_NULL = [(0, 0, 0), (255, 255, 255)]  # 미식별(검정)·배경(흰색) → null
CRISM_TOL2 = 60 * 60   # 최근접 프로토타입까지 허용 거리²(유클리드 ~60). 넘으면 혼합경계 노이즈 → null

def crism_nearest(r, g, b):
    """RGB 픽셀 → 최근접 범례색. (광물명, S1) 또는 미식별/배경/임계밖이면 (None, None)."""
    best_name, best_s, best_d = None, None, 1 << 30
    for R, G, B, name, s in CRISM_PROTOTYPES:
        d = (r - R) ** 2 + (g - G) ** 2 + (b - B) ** 2
        if d < best_d:
            best_d, best_name, best_s = d, name, s
    null_d = min((r - R) ** 2 + (g - G) ** 2 + (b - B) ** 2 for R, G, B in CRISM_NULL)
    if null_d < best_d or best_d > CRISM_TOL2:   # 검정/흰색이 더 가깝거나 너무 멀면 미식별
        return (None, None)
    return (best_name, best_s)

def crism_s1(r, g, b):
    """RGB 픽셀 → S1(0~4) 또는 None (단일 픽셀)."""
    return crism_nearest(r, g, b)[1]

# ── THEMIS 열관성(Thermal Inertia) → 암석 피복 rock(0~1) ────────────────────
# 출처: Zenodo 4931348 "THEMIS-derived Thermal Inertia of Jezero"(Edwards & Buz 2021).
#   단위 J·m⁻²·K⁻¹·s⁻¹ᐟ²(tiu), null=0. 낮은 TI=먼지/모래(입자 작고 느슨)=rock↓,
#   높은 TI=굳은 암석/바위(치밀)=rock↑.
# 기준값(Edwards & Buz 2021): ~150 느슨한 모래 / 350 굳은(indurated) 퇴적암 / >1200 결정질 화성암.
# 2구간 선형: 150→350 = rock 0→0.5(모래→굳은 퇴적암), 350→1200 = rock 0.5→1.0(→결정질 화성암).
ROCK_TI_DUST = 150.0   # 이 이하 = 느슨한 먼지/모래 → rock 0
ROCK_TI_MID  = 350.0   # 굳은 퇴적암(Edwards & Buz) → rock 0.5
ROCK_TI_HARD = 1200.0  # 결정질 화성암(Edwards & Buz) → rock 1.0

def rock_from_ti(ti):
    """열관성(TI) → 암석 피복 rock(0~1). 무효/0이면 None(가짜 안 채움)."""
    if ti is None or not (ti > 0):
        return None
    if ti <= ROCK_TI_DUST:
        return 0.0
    if ti <= ROCK_TI_MID:
        return round((ti - ROCK_TI_DUST) / (ROCK_TI_MID - ROCK_TI_DUST) * 0.5, 2)
    if ti <= ROCK_TI_HARD:
        return round(0.5 + (ti - ROCK_TI_MID) / (ROCK_TI_HARD - ROCK_TI_MID) * 0.5, 2)
    return 1.0

# ROC(Rank-Order Centroid) 기본 가중치 — weights.json 없을 때 내장 사용
ROC_DEFAULT = {"S1": 0.457, "S2": 0.257, "S4": 0.157, "S3": 0.09, "S5": 0.04}

def load_weights(path):
    try:
        w = json.load(open(path, encoding="utf-8"))
        m = {i["key"]: i["w_roc"] for i in w["indicators"]}
        return {k: m.get(k, 0.0) for k in ["S1", "S2", "S3", "S4", "S5"]}
    except Exception as e:
        print(f"[알림] weights.json 못읽음({e}) → 내장 ROC 기본값 사용(S1 .457 S2 .257 S4 .157 S3 .09 S5 .04)")
        return dict(ROC_DEFAULT)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dem", required=True)
    ap.add_argument("--out", default="grid.geojson")
    ap.add_argument("--weights", default="data/weights.json")
    ap.add_argument("--cell-px", type=int, default=25, help="칸=DEM 몇 픽셀(클수록 빠름)")
    ap.add_argument("--clip-km", type=float, default=0.0, help="기지서 이 거리(km) 안쪽 칸만 출력(데모용 경량화). 0=전체")
    ap.add_argument("--base-lat", type=float, default=18.44)
    ap.add_argument("--base-lon", type=float, default=77.45)
    ap.add_argument("--antenna-h", type=float, default=2.0)
    ap.add_argument("--crism", default=None, help="(선택) 함수광물 래스터 → S1")
    ap.add_argument("--geo", default=None, help="(선택) 퇴적/델타 래스터 → S2")
    ap.add_argument("--geo-scored", action="store_true",
                    help="--geo 래스터가 이미 S2(0~4) 점수면 퍼센타일 대신 footprint 평균 사용")
    ap.add_argument("--rock", default=None,
                    help="(선택) THEMIS 열관성 래스터 → 암석 피복 rock(0~1). 바위밭 A* 우회·안전레이어")
    args = ap.parse_args()

    try:
        import numpy as np
        import rasterio
        from rasterio.transform import xy
        from rasterio.warp import transform as rio_tf
        from rasterio.crs import CRS
    except ImportError:
        sys.exit("필요:  pip install rasterio numpy")

    GEO = CRS.from_proj4(f"+proj=longlat +R={MARS_R} +no_defs")
    ds = rasterio.open(args.dem)
    dem = ds.read(1).astype("float64")
    if ds.nodata is not None:
        dem[dem == ds.nodata] = np.nan
    H, W = dem.shape
    tr = ds.transform
    src = ds.crs or GEO
    is_geo = src.is_geographic
    print(f"DEM {W}x{H}, CRS={'위경도' if is_geo else '투영(미터)'}")

    # 픽셀 크기(m)
    if is_geo:
        midlat = (ds.bounds.top + ds.bounds.bottom) / 2
        px_m = abs(tr.a) * (MARS_R * math.pi / 180) * math.cos(math.radians(midlat))
    else:
        px_m = abs(tr.a)
    cell_m = px_m * args.cell_px
    print(f"픽셀≈{px_m:.1f}m, 칸≈{cell_m:.0f}m ({args.cell_px}px)")

    # 경사
    gy, gx = np.gradient(dem, px_m, px_m)
    slope = np.degrees(np.arctan(np.sqrt(gx**2 + gy**2)))

    # 기지(lon/lat) → DEM 원좌표 → 행열
    bxs, bys = rio_tf(GEO, src, [args.base_lon], [args.base_lat])
    inv = ~tr
    bcol, brow = inv * (bxs[0], bys[0])
    brow, bcol = int(round(brow)), int(round(bcol))
    base_z = (dem[brow, bcol] if (0 <= brow < H and 0 <= bcol < W)
              else np.nanmin(dem)) + args.antenna_h
    if not (0 <= brow < H and 0 <= bcol < W):
        print("[주의] 기지 좌표가 DEM 범위 밖 → 가시선은 최저점 기준 근사")

    opt = {}
    for key, p in [("S1", args.crism), ("S2", args.geo)]:
        if p:
            r = rasterio.open(p)
            cat = (r.count >= 3)          # 3밴드↑ uint8 RGB → 분류(categorical) 맵으로 간주
            scored = (key == "S2" and args.geo_scored)
            if cat:
                arr = r.read()[:3]        # (3, H, W) RGB
                print(f"[{key}] {p}: {r.count}밴드 RGB → 분류맵(범례 룩업) 사용")
            else:
                arr = r.read(1).astype("float64")
                if r.nodata is not None:
                    arr[arr == r.nodata] = np.nan
                print(f"[{key}] {p}: " + ("사전점수(0~4) → footprint 평균" if scored
                                           else "1밴드 연속형 → 퍼센타일 정규화") + " 사용")
            opt[key] = {"arr": arr, "inv": ~r.transform, "crs": r.crs or GEO, "cat": cat, "scored": scored}

    rock_opt = None
    if args.rock:
        rr = rasterio.open(args.rock)
        rarr = rr.read(1).astype("float64")
        rnd = rr.nodata
        if rnd is not None:
            rarr[rarr == rnd] = np.nan
        rock_opt = {"arr": rarr, "inv": ~rr.transform, "crs": rr.crs or GEO}
        print(f"[rock] {args.rock}: THEMIS 열관성 1밴드 → footprint 평균 TI → rock(0~1)")

    def sample_S(key, x, y):
        if key not in opt:
            return None
        o = opt[key]; arr, rinv, rcrs = o["arr"], o["inv"], o["crs"]
        xs, ys = rio_tf(src, rcrs, [x], [y])
        c, rr = rinv * (xs[0], ys[0]); c, rr = int(c), int(rr)
        if o["cat"]:                       # 분류맵: 중심 픽셀 RGB → 범례 룩업
            if 0 <= rr < arr.shape[1] and 0 <= c < arr.shape[2]:
                return crism_s1(int(arr[0, rr, c]), int(arr[1, rr, c]), int(arr[2, rr, c]))
            return None
        if 0 <= rr < arr.shape[0] and 0 <= c < arr.shape[1]:  # 연속형: 퍼센타일
            v = arr[rr, c]
            if np.isnan(v):
                return None
            lo, hi = np.nanpercentile(arr, 5), np.nanpercentile(arr, 95)
            return round(max(0, min(4, (v - lo) / (hi - lo + 1e-9) * 4)), 1)
        return None

    def sample_cat_mode(key, xmin, ymin, xmax, ymax):
        """칸 footprint(DEM-src bbox) 안 CRISM 픽셀들의 최빈 '광물 클래스' → S1.
        배경(흰)·미식별(검정)은 제외하고, 실제 광물이 하나라도 있으면 최빈 광물의 S1, 없으면 None."""
        if key not in opt:
            return None
        o = opt[key]
        if not o["cat"]:
            return sample_S(key, (xmin + xmax) / 2, (ymin + ymax) / 2)
        arr, rinv, rcrs = o["arr"], o["inv"], o["crs"]
        # bbox 네 꼭짓점을 CRISM crs로 투영 → 픽셀 행열 범위
        pxs, pys = rio_tf(src, rcrs, [xmin, xmax, xmin, xmax], [ymin, ymin, ymax, ymax])
        cols = [rinv * (px, py) for px, py in zip(pxs, pys)]
        rws = [col[1] for col in cols]; cls = [col[0] for col in cols]
        H2, W2 = arr.shape[1], arr.shape[2]
        c0 = max(0, int(math.floor(min(cls)))); c1 = min(W2, int(math.ceil(max(cls))) + 1)
        r0 = max(0, int(math.floor(min(rws)))); r1 = min(H2, int(math.ceil(max(rws))) + 1)
        if c0 >= c1 or r0 >= r1:
            return None
        sub = arr[:, r0:r1, c0:c1]
        counts = {}  # 광물명 → (픽셀수, S1)
        for yy in range(sub.shape[1]):
            for xx in range(sub.shape[2]):
                name, s = crism_nearest(int(sub[0, yy, xx]), int(sub[1, yy, xx]), int(sub[2, yy, xx]))
                if name is not None:
                    n0, _ = counts.get(name, (0, s)); counts[name] = (n0 + 1, s)
        if not counts:
            return None
        win = max(counts, key=lambda k: counts[k][0])  # 최빈 광물
        return counts[win][1]

    def sample_scored_mode(key, xmin, ymin, xmax, ymax):
        """사전점수(0~4) 래스터: 칸 footprint 안 유효 픽셀 평균 → S2. 유효 없으면 None."""
        if key not in opt:
            return None
        o = opt[key]; arr, rinv, rcrs = o["arr"], o["inv"], o["crs"]
        pxs, pys = rio_tf(src, rcrs, [xmin, xmax, xmin, xmax], [ymin, ymin, ymax, ymax])
        rc = [rinv * (px, py) for px, py in zip(pxs, pys)]
        cls = [p[0] for p in rc]; rws = [p[1] for p in rc]
        H2, W2 = arr.shape[0], arr.shape[1]
        c0 = max(0, int(math.floor(min(cls)))); c1 = min(W2, int(math.ceil(max(cls))) + 1)
        r0 = max(0, int(math.floor(min(rws)))); r1 = min(H2, int(math.ceil(max(rws))) + 1)
        if c0 >= c1 or r0 >= r1:
            return None
        sub = arr[r0:r1, c0:c1]
        vals = sub[~np.isnan(sub)]
        if vals.size == 0:
            return None
        return round(float(min(4.0, max(0.0, vals.mean()))), 1)

    def sample_rock(xmin, ymin, xmax, ymax):
        """칸 footprint 안 유효 열관성(TI>0) 평균 → rock(0~1). 유효 없으면 None."""
        if rock_opt is None:
            return None
        arr, rinv, rcrs = rock_opt["arr"], rock_opt["inv"], rock_opt["crs"]
        pxs, pys = rio_tf(src, rcrs, [xmin, xmax, xmin, xmax], [ymin, ymin, ymax, ymax])
        rc = [rinv * (px, py) for px, py in zip(pxs, pys)]
        cls = [p[0] for p in rc]; rws = [p[1] for p in rc]
        H2, W2 = arr.shape[0], arr.shape[1]
        c0 = max(0, int(math.floor(min(cls)))); c1 = min(W2, int(math.ceil(max(cls))) + 1)
        r0 = max(0, int(math.floor(min(rws)))); r1 = min(H2, int(math.ceil(max(rws))) + 1)
        if c0 >= c1 or r0 >= r1:
            return None
        sub = arr[r0:r1, c0:c1]
        vals = sub[np.isfinite(sub) & (sub > 0)]   # readme: null=0
        if vals.size == 0:
            return None
        return rock_from_ti(float(vals.mean()))

    def visible(crow, ccol, cz):
        n = max(abs(crow - brow), abs(ccol - bcol))
        if n == 0:
            return True
        steps = min(n, 256)                      # 비용 상한
        for i in range(1, steps):
            t = i / steps
            r = int(round(brow + (crow - brow) * t)); c = int(round(bcol + (ccol - bcol) * t))
            if 0 <= r < H and 0 <= c < W:
                terr = dem[r, c]
                if not np.isnan(terr) and terr > base_z + (cz - base_z) * t + 1.0:
                    return False
        return True

    W5 = load_weights(args.weights)
    feats = []
    cp = args.cell_px
    if args.clip_km > 0:                       # 기지 주변 픽셀 박스로 루프 제한(속도)
        cpx = int(args.clip_km * 1000 / px_m) + cp
        r_lo, r_hi = max(0, brow - cpx), min(H - cp, brow + cpx)
        c_lo, c_hi = max(0, bcol - cpx), min(W - cp, bcol + cpx)
    else:
        r_lo, r_hi, c_lo, c_hi = 0, H - cp, 0, W - cp
    dm = MARS_R * math.pi / 180
    for r0 in range(r_lo, r_hi, cp):
        for c0 in range(c_lo, c_hi, cp):
            blk = dem[r0:r0 + cp, c0:c0 + cp]
            if np.all(np.isnan(blk)):
                continue
            rc, cc = r0 + cp // 2, c0 + cp // 2
            cx, cy = xy(tr, rc, cc)
            clon, clat = rio_tf(src, GEO, [cx], [cy])
            if args.clip_km > 0:               # ★ 비싼 계산 전에 원형 clip
                dist = math.hypot((clat[0] - args.base_lat) * dm,
                                  (clon[0] - args.base_lon) * dm * math.cos(math.radians(args.base_lat)))
                if dist > args.clip_km * 1000:
                    continue
            z = float(np.nanmean(blk))
            slp = round(float(np.nanmean(slope[r0:r0 + cp, c0:c0 + cp])), 1)
            comm = "clear" if visible(rc, cc, z + args.antenna_h) else "shadow"
            xs, ys = [], []
            for rr, ccc in [(r0, c0), (r0, c0 + cp), (r0 + cp, c0 + cp), (r0 + cp, c0)]:
                x, y = xy(tr, rr, ccc); xs.append(x); ys.append(y)
            lon, lat = rio_tf(src, GEO, xs, ys)
            # S1: 분류맵 footprint 최빈 광물 / S2: 사전점수면 footprint 평균, 아니면 중심 샘플
            bb = (min(xs), min(ys), max(xs), max(ys))
            s1 = sample_cat_mode("S1", *bb)
            s2 = (sample_scored_mode("S2", *bb) if ("S2" in opt and opt["S2"]["scored"])
                  else sample_S("S2", cx, cy))
            S = {"S1": s1, "S2": s2, "S3": None, "S4": None, "S5": None}
            # score = 가용 지표만 재정규화: Σ(wᵢ·Sᵢ, 있는 i) / Σ(wᵢ, 있는 i) / 4 * 100
            # (지표가 하나도 없으면 null — 가짜 안 채움)
            score = None
            if W5:
                have = [k for k in S if S[k] is not None]
                wsum = sum(W5.get(k, 0.0) for k in have)
                if have and wsum > 0:
                    score = round(sum(W5.get(k, 0.0) * S[k] for k in have) / wsum / 4 * 100, 1)
            rock = sample_rock(*bb)   # 암석 피복(0~1) — 안전레이어(점수 아님)
            feats.append({
                "type": "Feature",
                "properties": {"slope_deg": slp, "comm": comm, **S, "score": score, "rock": rock},
                "geometry": {"type": "Polygon", "coordinates": [[
                    [round(lon[i], 6), round(lat[i], 6)] for i in range(4)] +
                    [[round(lon[0], 6), round(lat[0], 6)]]]}
            })

    out = {"type": "FeatureCollection",
           "_meta": {"cell_m": round(cell_m), "base": [args.base_lon, args.base_lat],
                     "note": "slope·comm=DEM 실데이터 / Sᵢ=래스터 준 것만(없으면 null)",
                     "score_note": "score=가용지표 재정규화, 현재 S1(CRISM 점토·탄산염)+S2(SIM3464 퇴적·델타) 기반",
                     "rock_note": "rock=THEMIS 열관성(Zenodo 4931348, Edwards&Buz 2021)→암석피복 0~1. 안전레이어(점수 아님), A* 간선비용·바위밭 우회",
                     "weights": W5},
           "features": feats}
    txt = json.dumps(out, ensure_ascii=False)
    if args.out.endswith(".js"):     # 더블클릭 데모용: window.GRID 전역
        txt = "window.GRID = " + txt + ";"
    open(args.out, "w", encoding="utf-8").write(txt)
    nn = sum(1 for f in feats if f["properties"]["score"] is not None)
    nr = sum(1 for f in feats if f["properties"].get("rock") is not None)
    print(f"칸 {len(feats)}개 → {args.out}  (경사·교신 채움 / 점수 채운 칸 {nn} / rock 채운 칸 {nr})")

if __name__ == "__main__":
    main()
