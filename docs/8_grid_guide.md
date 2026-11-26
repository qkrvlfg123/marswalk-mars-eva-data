# MARSWALK 격자 전처리 가이드 (grid.geojson)

> DEM 래스터를 칸별 속성표(GeoJSON)로 바꾸는 절차임. 한 번 실행하면 경사, 교신, 생명점수, 암석 피복이 칸 단위 실데이터로 채워짐.
> 스크립트: `scripts/build_grid.py`. 원본 래스터를 받아 둔 로컬 환경에서 실행함.

---

## 1. 산출물

칸마다 아래 속성을 가진 GeoJSON 을 만듦. 칸 크기는 DEM 픽셀 크기 × `--cell-px` 이고, 저장소의 격자는 CTX DEM 20m 에 `--cell-px 8` 을 써서 약 160m 임.

| 속성 | 뜻 | 출처 |
|---|---|---|
| `slope_deg` | 경사(도) | DEM 실데이터 |
| `comm` | `clear` / `shadow` (기지에서의 시선) | DEM 시선 판정 (지형 기반 추정) |
| `S1`~`S5` | 생명점수 지표 0~4 | 넣어 준 CRISM, 지질 래스터만 채점. 없으면 null |
| `score` | 생명점수 0~100 (ROC 가중) | 투입된 지표만 재정규화. 지표가 하나도 없으면 null |
| `rock` | 암석 피복 0~1 | `--rock` 으로 준 THEMIS 열관성. 없으면 null |

래스터를 주지 않은 지표는 `null` 로 남음. 없는 값을 채우지 않음.

## 2. 실행

저장소 루트에서 실행함.

```bash
pip install rasterio numpy

# 최소(DEM 만): 경사 + 교신. Sᵢ, score, rock 은 null
python scripts/build_grid.py --dem jezero_dem.tif --out grid.geojson --cell-px 8

# 저장소의 격자를 만든 명령(S1 + S2 + rock)
python scripts/build_grid.py --dem jezero_dem.tif \
  --crism zenodo_5575824/jezeroFinal.tif \
  --geo data/s2_jezero.tif --geo-scored \
  --rock zenodo_4931348/Jezero_Thermal_Inertia_v1.tiff \
  --out grid.js --clip-km 5 --cell-px 8 --antenna-h 15
```

| 옵션 | 기본값 | 뜻 |
|---|---|---|
| `--dem` | 필수 | DEM GeoTIFF |
| `--out` | `grid.geojson` | 출력 경로. `.js` 로 끝나면 `window.GRID = …;` 형태로 씀 |
| `--weights` | `data/weights.json` | 가중치 파일. 읽지 못하면 내장 ROC 기본값을 씀 |
| `--cell-px` | 25 | 칸 하나가 DEM 몇 픽셀인지. 실행하면 칸 크기(m)가 출력됨 |
| `--clip-km` | 0 (전체) | 기지에서 이 거리(km) 안쪽 칸만 출력 |
| `--base-lat`, `--base-lon` | 18.44, 77.45 | 기지 기준점. Perseverance 착륙지 |
| `--antenna-h` | 2.0 | 시선 판정에 쓰는 안테나 높이(m). 저장소 격자는 15 |
| `--crism` | 없음 | 광물 래스터 → S1 |
| `--geo` | 없음 | 퇴적, 델타 래스터 → S2 |
| `--geo-scored` | 꺼짐 | `--geo` 래스터가 이미 S2(0~4) 점수이면 칸 범위 평균을 씀 |
| `--rock` | 없음 | THEMIS 열관성 래스터 → rock(0~1) |

`grid.js` 와 `grid.geojson` 은 같은 내용임. 같은 명령을 `--out grid.geojson` 으로 한 번 더 실행하면 GeoJSON 판이 나옴.

## 3. 원본을 받는 곳

- DEM: 저장소 격자는 Jezero CTX DEM 20m (USGS Astrogeology)를 씀. Mars Trek (trek.nasa.gov/mars) 에서 Jezero 영역을 골라 DEM 을 받을 수도 있음.
  - 스크립트는 위경도 DEM 과 미터 투영 DEM 을 모두 처리함. 출력은 lon/lat 임.
- 고해상도(델타): USGS, PDS 의 HiRISE, CTX DTM.
- 광물(S1): CRISM 광물맵 Zenodo 5575824. 지질(S2): USGS SIM 3464 를 `scripts/make_s2.py` 로 재코딩한 `data/s2_jezero.tif`.
- 링크는 `docs/6_raw_downloads.md` 에 있음.

## 4. 처리 시간 (초기 작업 때의 대략값)

| 작업 | 시간 |
|---|---|
| DEM 다운로드 + 경사, 교신 | 약 40분~1.5시간 |
| CRISM, 지질까지 Sᵢ | 추가 1~3시간 |

## 5. 앱 연동

```js
// Leaflet
fetch('grid.geojson').then(r=>r.json()).then(g=>{
  L.geoJSON(g, { style: f => ({
    fillColor: colorByScore(f.properties.score),       // 생명점수 히트맵
    fillOpacity: f.properties.comm==='shadow' ? 0.15 : 0.5,  // 교신 음영은 흐리게
    color: f.properties.slope_deg>25 ? '#e55' : '#555' // 급경사 테두리(통행 불가)
  })}).addTo(map);
});
```

- 안전 게이트: `slope_deg>25` 또는 복귀선 밖이면 잠금(회색). `comm==='shadow'` 이면 교신 경고(참고용).
- `marswalk_grid_demo.html` 은 `fetch` 대신 `<script src="grid.js">` 로 `window.GRID` 를 읽음.

## 6. 주의

- `slope_deg`, `comm` 은 DEM 실데이터 기반임. `comm` 은 지형 시선만 판정하고 전파 세기와 중계 위성은 반영하지 않음. 교신 음영(지형 기반 추정)으로 표기하고 측정 전파가 아님을 밝힘.
- CRISM 처럼 3밴드 이상인 RGB 래스터는 범례 색 룩업으로 채점함. 1밴드 연속형 래스터를 `--geo-scored` 없이 넣으면 5~95 퍼센타일 정규화로 0~4 를 매기는데, 이 방식은 예시 수준이라 실제 단위에 맞춘 루브릭 고정이 필요함.
- 가중치(ROC)는 데이터가 아니라 순위 기반 공식값임(`docs/7_biosignature_design.md` 참고).
