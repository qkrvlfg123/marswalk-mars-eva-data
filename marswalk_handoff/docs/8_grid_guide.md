# MARSWALK — 격자 전처리 가이드 (grid.geojson)

> "그림(DEM 래스터)" → "칸별 숫자표(geojson)". 이거 한 번이면 **경사·교신·생명점수 셀** 3개가 전부 실데이터 기반이 됨.
> 스크립트: `scripts/build_grid.py` (로컬 실행 — 워크스페이스는 NASA 접속 불가).

---

## 1. 뭘 만드나

칸(기본 ~100m)마다 이 속성이 박힌 GeoJSON:

| 속성 | 뜻 | 출처 |
|---|---|---|
| `slope_deg` | 경사(도) | DEM 실데이터 |
| `comm` | `clear`/`shadow` (기지 가시선) | DEM 가시선(지형 기반 추정) |
| `S1..S5` | 생명점수 지표 0~4 | CRISM/지질 래스터 준 것만, **없으면 null** |
| `score` | 생명점수 0~100 (ROC 가중합) | Sᵢ 다 있을 때만 |

**정직성:** 래스터 안 주면 Sᵢ는 `null`. 가짜값 안 채움.

## 2. 실행

```bash
pip install rasterio numpy

# 최소(DEM만) → 경사 + 교신 활성, Sᵢ는 null
python scripts/build_grid.py --dem jezero_dem.tif --out data/grid.geojson --cell-px 8

# 풀(광물까지) → 생명점수 셀까지
python scripts/build_grid.py --dem jezero_dem.tif --crism clay.tif --geo delta.tif \
       --out data/grid.geojson --cell-px 8
```
- `--cell-px` : 칸 하나 = DEM 몇 픽셀(실행 시 칸 크기 m 출력됨). DEM 해상도 보고 100m 맞게 조정.
- `--base-lat/lon` : 기지 기준점. 기본값 = Perseverance 착륙지 18.44N 77.45E.

## 3. DEM 받는 곳

- **Mars Trek** (trek.nasa.gov/mars) → Jezero 영역 선택 → Download → DEM.
  - 투영 **Equirectangular(lon/lat, 도 단위)**로 받으면 좌표변환 없이 바로 됨.
- 고해상도(델타): USGS/PDS HiRISE·CTX DTM.
- 광물(S1): CRISM 함수광물 지도 / 지질(S2): USGS SIM3464.

## 4. 처리 시간 (대략)

| 작업 | 시간 |
|---|---|
| DEM 다운 + 경사·교신 | ~40분~1.5시간 |
| CRISM/지질까지 Sᵢ | +1~3시간 |

## 5. 앱 연동

```js
// Leaflet
fetch('data/grid.geojson').then(r=>r.json()).then(g=>{
  L.geoJSON(g, { style: f => ({
    fillColor: colorByScore(f.properties.score),       // 생명점수 히트맵
    fillOpacity: f.properties.comm==='shadow' ? 0.15 : 0.5,  // 교신 음영 흐리게
    color: f.properties.slope_deg>25 ? '#e55' : '#555' // 급경사 테두리(통행불가)
  })}).addTo(map);
});
```
- 안전 게이트: `slope_deg>25` 또는 복귀선 밖 → 잠금(회색). `comm==='shadow'` → 🔴 교신 경고(참고용).

## 6. 주의 (정직하게)

- `slope_deg`·`comm` = **DEM 실데이터 기반**. `comm`은 지형 가시선만 — 전파세기·중계위성 미반영 → "교신 음영(지형 기반 추정)"으로 표기, "측정 전파" 아님.
- `Sᵢ`의 0~4 변환은 래스터 스케일에 맞춰 보정 필요(스크립트는 5~95퍼센타일 정규화 예시). CRISM 광물맵 실제 단위 확인 후 루브릭 고정 권장.
- 가중치(ROC)는 데이터 아님 — 순위 기반 공식값(`MARSWALK_생명점수_상세설계` 참고).
