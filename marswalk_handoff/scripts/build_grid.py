#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MARSWALK 격자 전처리 — DEM → grid.geojson
"그림(래스터)"을 "칸별 숫자표"로 바꾼다. 앱은 이 geojson을 읽어 칸을 색칠.

칸마다 계산:
  - slope_deg : 경사 (안전 레이어 + 대사율 η 입력)
  - comm      : 기지에서 보이나(가시선) → 교신 음영 (지형 기반 추정)
  - S1..S5    : 생명점수 지표 0~4 (CRISM/지질 래스터 주면 채움, 없으면 null)
  - score     : 생명점수 0~100 (weights.json ROC로 가중합; Sᵢ 있을 때만)

실행(로컬):
  pip install rasterio numpy
  python build_grid.py --dem jezero_dem.tif --out ../data/grid.geojson --cell-px 8
  # (선택) --crism clay.tif --geo delta.tif  로 Sᵢ 채우기

중요(정직성): 래스터 안 주면 해당 Sᵢ는 null로 남긴다. 절대 가짜값 안 채움.

DEM 받는 곳:
  - Mars Trek (trek.nasa.gov/mars) → Jezero 영역 → Download → DEM, 투영 "Equirectangular(lon/lat)" 권장
  - 또는 USGS/PDS HiRISE·CTX DTM (고해상도 델타)
  * lon/lat(도 단위) GeoTIFF로 받으면 좌표 변환 없이 바로 됨.
"""
import argparse, json, math, sys

def load_weights(path):
    """weights.json에서 ROC 가중치를 S1..S5 순서로."""
    try:
        w = json.load(open(path, encoding="utf-8"))
        m = {i["key"]: i["w_roc"] for i in w["indicators"]}
        return {k: m.get(k, 0.0) for k in ["S1", "S2", "S3", "S4", "S5"]}
    except Exception as e:
        print(f"[경고] weights.json 못읽음({e}) → score 계산 생략")
        return None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dem", required=True, help="DEM GeoTIFF 경로 (lon/lat 권장)")
    ap.add_argument("--out", default="grid.geojson")
    ap.add_argument("--weights", default="data/weights.json")
    ap.add_argument("--cell-px", type=int, default=8, help="칸 하나 = DEM 몇 픽셀(집계 배수)")
    ap.add_argument("--base-lat", type=float, default=18.44, help="기지 위도(Perseverance 착륙지)")
    ap.add_argument("--base-lon", type=float, default=77.45, help="기지 경도")
    ap.add_argument("--antenna-h", type=float, default=2.0, help="기지 안테나/대원 눈높이 m")
    ap.add_argument("--crism", default=None, help="(선택) 함수광물 래스터 → S1")
    ap.add_argument("--geo", default=None, help="(선택) 퇴적/델타 래스터 → S2")
    args = ap.parse_args()

    try:
        import numpy as np
        import rasterio
        from rasterio.transform import xy
    except ImportError:
        sys.exit("rasterio/numpy 필요 →  pip install rasterio numpy")

    ds = rasterio.open(args.dem)
    dem = ds.read(1).astype("float64")
    dem[dem == ds.nodata] = np.nan
    H, W = dem.shape
    tr = ds.transform
    # 픽셀 크기(도) → m (화성 반지름 3389.5km)
    R = 3389500.0
    deg2m_lat = R * math.pi / 180.0
    px_deg = abs(tr.a)                      # 경도 픽셀 크기(도)
    midlat = ds.bounds.top*0.5 + ds.bounds.bottom*0.5
    px_m = px_deg * deg2m_lat * math.cos(math.radians(midlat))
    cell_m = px_m * args.cell_px
    print(f"DEM {W}x{H}, 픽셀≈{px_m:.1f}m, 칸≈{cell_m:.0f}m ({args.cell_px}px)")

    # 경사(도): numpy gradient, 미터 간격
    gy, gx = np.gradient(dem, px_m, px_m)
    slope = np.degrees(np.arctan(np.sqrt(gx**2 + gy**2)))

    # 기지 픽셀 위치
    inv = ~tr
    bcol, brow = inv * (args.base_lon, args.base_lat)
    brow, bcol = int(brow), int(bcol)
    base_z = (dem[brow, bcol] if (0 <= brow < H and 0 <= bcol < W) else np.nanmin(dem)) + args.antenna_h

    W5 = load_weights(args.weights)
    opt = {}
    for key, p in [("S1", args.crism), ("S2", args.geo)]:
        if p:
            r = rasterio.open(p)
            opt[key] = (r.read(1).astype("float64"), ~r.transform, r)

    def sample_S(key, lon, lat):
        """래스터값 → 0~4. (실제 광물맵 스케일에 맞게 조정 필요; 여기선 정규화 예시)"""
        if key not in opt:
            return None
        arr, rinv, r = opt[key]
        c, rr = rinv * (lon, lat)
        c, rr = int(c), int(rr)
        if 0 <= rr < arr.shape[0] and 0 <= c < arr.shape[1]:
            v = arr[rr, c]
            if np.isnan(v):
                return None
            lo, hi = np.nanpercentile(arr, 5), np.nanpercentile(arr, 95)
            return round(max(0, min(4, (v-lo)/(hi-lo+1e-9)*4)), 1)
        return None

    def visible(crow, ccol, cz):
        """기지→칸 가시선: 중간 지형이 직선보다 높으면 가림(교신 끊김)."""
        n = max(abs(crow-brow), abs(ccol-bcol))
        if n == 0:
            return True
        for i in range(1, n):
            t = i/n
            r = int(round(brow+(crow-brow)*t)); c = int(round(bcol+(ccol-bcol)*t))
            if not (0 <= r < H and 0 <= c < W):
                continue
            terr = dem[r, c]
            if np.isnan(terr):
                continue
            # 직선 높이 vs 지형 높이 (거리 비례 보간)
            line_z = base_z + (cz-base_z)*t
            if terr > line_z + 1.0:      # 1m 여유
                return False
        return True

    feats = []
    for r0 in range(0, H-args.cell_px, args.cell_px):
        for c0 in range(0, W-args.cell_px, args.cell_px):
            blk = dem[r0:r0+args.cell_px, c0:c0+args.cell_px]
            if np.all(np.isnan(blk)):
                continue
            rc, cc = r0+args.cell_px//2, c0+args.cell_px//2
            lon, lat = xy(tr, rc, cc)
            z = float(np.nanmean(blk))
            slp = round(float(np.nanmean(slope[r0:r0+args.cell_px, c0:c0+args.cell_px])), 1)
            comm = "clear" if visible(rc, cc, z+args.antenna_h) else "shadow"
            S = {k: sample_S(k, lon, lat) for k in ["S1", "S2"]}
            S.update({"S3": None, "S4": None, "S5": None})
            score = None
            if W5 and all(S[k] is not None for k in S):
                score = round(sum(W5[k]*S[k] for k in S)/4*100, 1)
            # 칸 폴리곤(도)
            x0, y0 = xy(tr, r0, c0); x1, y1 = xy(tr, r0+args.cell_px, c0+args.cell_px)
            feats.append({
                "type": "Feature",
                "properties": {"slope_deg": slp, "comm": comm, **S, "score": score},
                "geometry": {"type": "Polygon", "coordinates": [[
                    [x0, y0], [x1, y0], [x1, y1], [x0, y1], [x0, y0]]]}
            })

    out = {"type": "FeatureCollection",
           "_meta": {"cell_m": round(cell_m), "base": [args.base_lon, args.base_lat],
                     "note": "slope·comm=DEM 실데이터 / Sᵢ=래스터 준 것만(없으면 null, 가짜 안채움)",
                     "weights": "ROC (weights.json)"},
           "features": feats}
    json.dump(out, open(args.out, "w", encoding="utf-8"), ensure_ascii=False)
    nonull = sum(1 for f in feats if f["properties"]["score"] is not None)
    print(f"칸 {len(feats)}개 → {args.out}  (경사·교신 채움 / 점수 채운 칸 {nonull})")

if __name__ == "__main__":
    main()
