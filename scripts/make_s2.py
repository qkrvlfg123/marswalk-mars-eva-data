#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""USGS SIM3464 Jezero-Nili 지질맵(GeoUnits_v1 폴리곤) → S2(퇴적·델타) 래스터.

S2 = 세립 퇴적/델타·호성 유닛일수록 높게(0~4). 근거: Broz et al. (2020),
'Experimental investigation of clay-rich, fine-grained lacustrine/deltaic sediments
의 유기물 보존능': 미세립 점토질 호성/삼각주 퇴적물이 유기물 보존에 가장 유리.
델타 팬(삼각주 퇴적) > 평활 퇴적평원 > 호저(저지 평탄) > 기반암/풍성사 > 충돌/노출암.

출력: data/s2_jezero.tif (float32, nodata=-1), CRS=MTM_clon77.5E(지질맵 원본).

실행(저장소 루트에서, 입력·출력 경로가 실행 위치 기준): python scripts/make_s2.py
"""
import sys, numpy as np, rasterio
from rasterio.transform import from_origin
from rasterio.features import rasterize
from rasterio.crs import CRS
import pyogrio, shapely

GDB = r"sim3464_extract/sim3464_JezeroNili_FINAL/Geodatabase/Nili.gdb"
LAYER = "GeoUnits_v1"
OUT = "data/s2_jezero.tif"
RES = 50.0   # m/px

# 지질유닛(name) → S2(0~4)  [SIM3464, Sun & Stack 2020 유닛명]
NAME2S2 = {
    "Jezero fan 1 unit":     4,  # 서부 삼각주 퇴적(세립 델타), 최상위 보존 타깃
    "Jezero fan 2 unit":     4,
    "Nili Planum fan unit":  4,
    "Smooth unit, undivided":3,  # 평활 퇴적평원(세립 가능)
    "Jezero floor unit":     1,  # 호저 저지 평탄부. Perseverance 착륙 후 화성암(Máaz/Séítah)으로 확인(퇴적 아님) → 하향
    "Upper etched unit":     1,  # Nili Planum 탄산염·올리빈 노출 기반암(비호성)
    "Lower etched unit":     1,
    "Nili Planum 1 unit":    1,  # 고지 기반암/평원
    "Nili Planum 2 unit":    1,
    "Eolian bedform unit":   1,  # 풍성 사구(재이동 조립 → 보존 불리)
    "Rugged bright unit":    0,
    "Crater rim unit":       0,  # 충돌 기원 → 퇴적 보존 없음
    "Crater riim unit":      0,  # (원본 오타 변형)
    "Crater ejecta unit":    0,
    "Crater interior unit":  0,
}

def main():
    import os
    os.makedirs("data", exist_ok=True)
    info = pyogrio.read_info(GDB, layer=LAYER)
    crs_wkt = info["crs"]
    r = pyogrio.raw.read(GDB, layer=LAYER, read_geometry=True, columns=["name"])
    meta, geoms_wkb, field_data = r[0], r[2], r[3]   # (meta, fids, geometry, field_data)
    cols = list(meta["fields"]); names = field_data[cols.index("name")]

    # WKB → shapely, (geom, S2) 리스트. 미지정 유닛은 제외(nodata로 남김)
    shapes, miss = [], {}
    xmin = ymin = 1e18; xmax = ymax = -1e18
    for wkb, nm in zip(geoms_wkb, names):
        s2 = NAME2S2.get(str(nm))
        if s2 is None:
            miss[str(nm)] = miss.get(str(nm), 0) + 1
            continue
        g = shapely.from_wkb(bytes(wkb))
        if g.is_empty:
            continue
        shapes.append((g.__geo_interface__, float(s2)))
        x0, y0, x1, y1 = g.bounds
        xmin, ymin, xmax, ymax = min(xmin, x0), min(ymin, y0), max(xmax, x1), max(ymax, y1)
    if miss:
        print("[제외된 유닛(S2 미지정)]", miss)

    # 높은 S2가 겹침 시 우선 burn되도록 오름차순 정렬
    shapes.sort(key=lambda s: s[1])
    W = int(np.ceil((xmax - xmin) / RES)); H = int(np.ceil((ymax - ymin) / RES))
    transform = from_origin(xmin, ymax, RES, RES)
    arr = rasterize(shapes, out_shape=(H, W), transform=transform,
                    fill=-1.0, dtype="float32", all_touched=False)
    prof = dict(driver="GTiff", width=W, height=H, count=1, dtype="float32",
                crs=CRS.from_wkt(crs_wkt), transform=transform, nodata=-1.0, compress="deflate")
    with rasterio.open(OUT, "w", **prof) as dst:
        dst.write(arr, 1)
    valid = arr[arr >= 0]
    print(f"{OUT}: {W}x{H} @ {RES:.0f}m, 유닛폴리곤 {len(shapes)}개 burn")
    print(f"유효 픽셀 {valid.size} / S2 분포:",
          {int(v): int((valid == v).sum()) for v in sorted(set(valid.tolist()))})

if __name__ == "__main__":
    main()
