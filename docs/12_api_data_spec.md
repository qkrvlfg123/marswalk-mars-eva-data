# MARSWALK 데이터, API 계약서 (Data & API Spec) (2026-11-15)

> 목적: 프론트 개발자가 이 문서만으로 React + Leaflet + Recharts + Zustand 로 데모를 다시 구현할 수 있게 하는 계약서임.
> 원칙: 실제 산출 파일(`grid.geojson`, `data/*.json`, `marswalk_grid_demo.html`)에서 읽은 내용만 기록함. 문서 끝 §10 에 코드 대조 결과가 있음.
> 좌표 규약은 §1 에서 먼저 확인해야 함. GeoJSON 은 `[lon,lat]`, 앱 내부(Leaflet, BASE, SPOTS, 경로)는 `[lat,lon]` 임. 섞으면 지도가 뒤집힘.

---

## 0. 런타임 흐름 (fetch → store → tick → render)

```
1) 로드    fetch('grid.geojson')  →  { type:'FeatureCollection', _meta, features[3067] }
           fetch('data/*.json')   →  상수, 스펙, 지점
2) 파생    features → cells[]  (칸 중심 centroid + slope/comm/score/rock)   ← 발밑 조회, A* 노드
           features → graph   (buildGraph: 투영 좌표 + 8이웃 인접 리스트)   ← 1회 캐시
3) 선택    setTarget(spot)    →  computePath(target, load)  →  PATH[], PATHlen, reachable
4) 틱      setInterval(step, 120ms)  →  walked 누적 → 위치, 소모품, 경사, 상태 갱신
5) 렌더    store 구독 → 패널(산소, 체력, 피폭, 심박) + 지도(대원 마커, 복귀선 ring, 경로 polyline)
```

- 틱 주기는 120 ms 임. 한 틱에 `walked`(기지로부터 경로 이동거리, m)가 6 m 씩 변함(전진 +, 복귀 −). 재생 속도는 실제 EVA 시간이 아니라 데모 가속 스케일임(아래 상수 `speed*3*2`).
- 복귀 트리거: `walked ≥ min(목표거리, 복귀선 반경)` 이면 `returning=true`. `walked ≤ 0` 이고 산소가 만충의 99% 미만이면 EVA 종료(`done=true`, 타이머 정지).
- 격자가 없을 때의 폴백: `window.GRID`(= grid.geojson 내용)가 없으면 경사는 수동 슬라이더, 경로는 직선 보간을 씀. 앱은 이 경우에도 동작해야 함.
- 현재 데모는 `fetch('grid.geojson')` 대신 `<script src="grid.js">` 로 격자를 읽고, `data/*.json` 중에서는 `donki_sample.json` 만 fetch 함. 지점은 HTML 안에 인라인으로 있음.

---

## 1. 좌표, 단위 규약

| 맥락 | 순서 | 예 | 비고 |
|---|---|---|---|
| grid.geojson geometry | `[lon, lat]` | `[77.4323, 18.5240]` | GeoJSON 표준 (RFC 7946) |
| 앱 내부 좌표 (BASE, SPOTS, PATH, Leaflet) | `[lat, lon]` | `[18.44, 77.45]` | Leaflet `LatLng` 관례 |
| 각도 | 십진도 (deg) | lon 77.4, lat 18.4 | Jezero (화성) |
| 거리 | 미터 (화성 반지름 기준) | 없음 | 지구 반지름을 쓰지 않음. §5.3 `marsDist` 사용 |
| 경사 `slope_deg` | 도 (°) | 0.5~22.7 | |
| 생명점수 `score` | 0~100 | 25~100 | |

- 화성 거리 상수: `MARS_R = 3396190 m` (USGS 3396.19 km). `DEGLAT_M = MARS_R·π/180 ≈ 59,275 m/°`.
- 거리식(등장방형 근사, 고정 위도): `kx = cos(18.44°)·DEGLAT_M`, `dist = hypot((Δlon)·kx, (Δlat)·DEGLAT_M)`. 위도 18.44° 를 상수로 고정함(칸별로 cos 를 다시 계산하지 않음). Jezero 국소 영역이라 오차는 무시할 수 있음. Leaflet `map.distance()` 는 지구 반지름을 쓰므로 사용하지 않음(약 1.88배 크게 나옴).

---

## 2. `grid.geojson` 계약 (메인 데이터)

- 최상위: `{ "type": "FeatureCollection", "_meta": {…}, "features": [3067] }`
- 각 feature: `{ "type":"Feature", "properties":{…}, "geometry":{…} }`
- geometry: Polygon, 링 1개, 점 5개(사각 칸, 첫 점과 마지막 점이 같음). 칸 크기 약 160 m.

### 2.1 `properties` 스키마 (전 3,067칸 집계)

| 필드 | 타입 | 단위/범위 | null | 의미 |
|---|---|---|---|---|
| `slope_deg` | number (float) | 0.5~22.7 ° | 없음 (0/3067) | DEM 경사. 안전 게이트(25° 초과 통행 불가. 이 격자에는 25 초과 칸이 없음) |
| `comm` | string | `"clear"` \| `"shadow"` | 없음 | 기지에서 칸까지의 시선 교신. shadow 는 음영. (clear 2,483 / shadow 584) |
| `S1` | number (int) | 1~4 (관측값 {1,3,4}) | 579칸 null | 함수/점토광물 지표. CRISM. null 은 미식별(검정), 배경(흰색) |
| `S2` | number (float) | 0.2~4.0 | 없음 | 퇴적, 델타 지표. SIM 3464. 칸 범위 평균이라 소수가 나옴 |
| `S3` | null | 없음 | 전부 null | 보존성 염류. 설계 완료, 미적용 (Jezero 에 드묾). `docs/9_verification_status.md` |
| `S4` | null | 없음 | 전부 null | 물 활동. 설계 완료, 미적용 (S1, S2 에 내재) |
| `S5` | null | 없음 | 전부 null | 로버 근접. 미투입 |
| `score` | number (float) | 25.0~100.0 | 없음 | 생명점수 (가용 지표 재정규화, §6). 전 칸 채움 |
| `rock` | number (float) | 0.0~1.0 (이 격자 관측 0.0~0.32) | TI 무효 칸만 (이 격자 null 0) | 암석 피복 (THEMIS 열관성 → rock). 안전 레이어(점수 아님), A* 바위밭 우회. 0 은 먼지/모래, 1 은 바위/화성암 |

> 프론트 주의: `Sᵢ` 는 null 일 수 있거나(S1) 항상 null 임(S3, S4, S5). 숫자로 가정하지 않음. `v == null ? '-' : v` 로 처리함. `score`, `rock` 은 이 격자에서는 항상 숫자지만 `rock` 도 일반적으로 null 이 될 수 있음(TI=0 nodata).

### 2.2 `_meta` (실제 내용)

```json
{
  "cell_m": 160,
  "base": [77.45, 18.44],
  "note": "slope·comm=DEM 실데이터 / Sᵢ=래스터 준 것만(없으면 null)",
  "score_note": "score=가용지표 재정규화, 현재 S1(CRISM 점토·탄산염)+S2(SIM3464 퇴적·델타) 기반",
  "rock_note": "rock=THEMIS 열관성(Zenodo 4931348, Edwards&Buz 2021)→암석피복 0~1. 안전레이어(점수 아님), A* 간선비용·바위밭 우회",
  "weights": { "S1":0.457, "S2":0.257, "S4":0.157, "S3":0.09, "S5":0.04 }
}
```

- `_meta.base` 는 `[lon,lat]` 순서임(geometry 와 같은 규약). Perseverance 착륙지이고, 앱의 `BASE` 는 `[lat,lon]=[18.44,77.45]` 임.
- `_meta.weights`: S4=0.157 (순위 3, 물 활동), S3=0.09 (순위 4, 염류). 번호와 순위가 다름(ROC 는 순위로 가중치를 정함). score 계산에 쓰는 가중치 기준값임.

---

## 3. `data/*.json` 계약 (상수, 스펙, 지점)

### 3.1 `spots.json` 탐사 지점 (배열), `spots.js` 같은 데이터의 스크립트판

| 필드 | 타입 | 단위 | 의미 |
|---|---|---|---|
| `name` | string | 없음 | 지점명 (목적지 식별 키) |
| `lat` | number | deg | 위도 |
| `lon` | number | deg | 경도 |
| `score` | number | 0~100 | 폴백용 초기 추정값. 실제 표시는 런타임에 격자 최근접 칸의 score 로 대체됨 (§5.4 `spotScore`) |
| `note` | string | 없음 | 설명 |
| `img` | string (URL) | 없음 | Perseverance raw 실사 URL (mars.nasa.gov) |

지점은 4개임: 델타 전선, Cheyava 방향, Hawksbill Gap, Séítah. `spots.js` 는 최상위 `const SPOTS=[…]` 로 선언함. 데모 HTML 은 이 파일을 불러오지 않고 같은 좌표, 점수, 이미지 URL 을 인라인으로 가지고 있으며 `note` 문구만 일부 다름.

### 3.2 `crew_spec.json` 대원 제원

| 경로 | 값 | 단위 | 의미 |
|---|---|---|---|
| `age.value` | 34 | yr | 나이 (HRmax 계산용) |
| `weight_kg.value` | 80 | kg | 체중 = Pandolf `M` |
| `vo2peak.value` | 37.5 | ml/kg/min | 최대산소섭취량 |
| `sustainable_pct.value` | 0.35 | 비율 | 지속가능 작업률 = `SUSTAIN` |
| `hr_model.formula` | `"HR = 70.5 + 113.2*pctVO2"` | 없음 | PhysioNet 보정 (R²=0.77) |
| `hrmax.value` | 186 | bpm | `220-age` |

### 3.3 `consumables.json` EVA 소모품

| 경로 | 값 | 의미 |
|---|---|---|
| `nominal_duration_min` | 480 | 공칭 지속 시간 (분) |
| `nominal_metabolic_BTU_hr` | 930 | 공칭 대사율 |
| `duration_vs_workload[]` | `{BTU_hr, hours}` 3개 | 대사율과 지속시간 곡선 (930/8h, 1200/6h, 1600/5h) |
| `consumables[]` | `{key,name,capacity,scales_with_metabolic,source}` | o2/fw/co/ba 4종. `capacity` 는 문자열임 (단위 포함, 예 `"1430 psi"`) |

> 주의: `capacity` 는 숫자가 아니라 단위가 붙은 문자열이라 파싱이 필요함. `scales_with_metabolic` 만 boolean 임.

### 3.4 `radiation.json` 피폭 상수

| 경로 | 값 | 단위 | 의미 |
|---|---|---|---|
| `baseline_mSv_per_day` | 0.64 | mSv/day | 기준 선량 = `RAD_DAY` |
| `spe_spike_mSv` | `[1.2, 19.5]` | mSv | SPE 스파이크 범위 |
| `terrain_shielding_max_pct` | 20 | % | 지형 차폐 최대 |
| `xray_equiv_mSv` | 0.1 | mSv | 흉부 X선 1장 환산 |
| `donki_api` | URL | 없음 | 우주기상 라이브 |

### 3.5 `synthetic_eva.json` Recharts 용 시계열

`scenario[]` 의 각 원소가 한 시점임.

| 필드 | 타입 | 단위 |
|---|---|---|
| `t_min` | int | 분 (0, 10, …, 50) |
| `slope_deg` | number | ° |
| `load_kg` | number | kg |
| `pctVO2` | number | 0~1+ (1 초과는 지속 불가) |
| `HR_bpm` | int | bpm |
| `O2_Lmin` | number | L/min |
| `sustainable` | boolean | pctVO2 ≤ 1 여부 |

Recharts `<LineChart data={scenario}>` 에 그대로 넣을 수 있음(x=`t_min`, y=`HR_bpm`, `O2_Lmin`, `pctVO2`). 최상위에 설명용 `_source`, `_model`, `_sustainable_def` 문자열이 함께 있음.

### 3.6 `weights.json` 생명점수 가중치와 지표 정의

- `indicators[]`: `{key, rank, name, layer, why, src, w_roc, w_rs}`. key 는 S1, S2, S4, S3, S5 이고 rank 는 1~5.
- rank 3 이 S4(물 활동, w_roc 0.157), rank 4 가 S3(염류, w_roc 0.09)임. grid `_meta.weights` 와 일치함.
- `presets_rank`: 순위 재배열 프리셋 3종(과학권장, 물추적, 검증우선). UI 는 숫자 입력이 아니라 순위 드래그로 다시 계산함.

### 3.7 `layers.json` 지도 레이어 정의

- `science_layers.items[]` (S1, S2, S4, S3, S5 각 `{feeds,name,product,source,rubric,status}`) 와 `safety_layers.items[]` (walkback/slope/rock/rad/comm, `{key,name,product,source,gate}` 와 일부 항목의 `status`, `base`).
- `rock` 안전 레이어는 THEMIS 열관성(Zenodo 4931348)에서 만든 grid `rock` 필드임. gate 는 SOFT(A* 비용 ×(1+2·rock) 로 우회)이고 점수에는 합산하지 않음. 지도 레이어 5종 중 열(thermal) 레이어에 해당함.
- 안전 레이어는 점수에 합산하지 않고 게이트로만 씀. `_combine`: `recommend = gate_hard ? 0 : score × soft_penalty`.
- 데모와 스크립트는 이 파일을 읽지 않음. 설계 정의용 파일임.

### 3.8 `donki_sample.json` 우주기상 리플레이 샘플

- `event{messageType:"FLR", messageIssueTime, note}`. 실제 운용에서는 DONKI 라이브를 씀.
- `spe{active, onset_tick, duration_ticks, spike_mSv, shield_max_pct, alert, _note}`. 데모가 fetch 해서 SPE 활성 구간과 차폐율로 씀. 파일을 읽지 못하면(HTML 을 파일로 직접 연 경우) 같은 값의 인라인 기본값을 씀.

### 3.9 `equipment.json` 적재 하중 L 기준표

- `items[]`: `{name, kg, src}` (HTC 13.4, ALSRC 6.7 등, Apollo 문서값). `apollo_tool_totals_kg` (임무별 22.9~53.0). `plss_kg.value` 47. `_default_L_kg` 20. Pandolf `L` 입력의 근거임. 상세는 `docs/2_sources.md`.

---

## 4. 모델 상수 (marswalk_grid_demo.html 의 실제 값)

| 상수 | 값 | 단위 | 의미 |
|---|---|---|---|
| `M` | 80 | kg | 체중 (Pandolf 기준 질량) |
| `VO2ABS` | 3.0 | L/min | 절대 최대 산소섭취량 (pct 분모) |
| `ETA` (η) | 2.0 | 없음 | 지형계수 (레골리스를 모래로 근사) |
| `GMARS` | 0.38 | 없음 | 화성 중력비 |
| `O2W` | 1/348 | (L/min)/W | 대사율(W) → 산소 소모율 환산 |
| `SUSTAIN` | 0.35 | 없음 | 지속가능 작업률 임계 |
| `HR_A` | 70.5 | bpm | 심박식 절편 (PhysioNet 보정) |
| `HR_B` | 113.2 | bpm | 심박식 기울기 (%VO₂ 1.0 당 증가분) |
| `HRMAX` | 186 | bpm | 최대 심박 (220 − 34), 심박 상한 |
| `TANK` | 500 | L | 산소 탱크 용량 (= 100%) |
| `RAD_DAY` | 0.64 | mSv/day | 일일 피폭 기준 |
| `MAXWB` | 2000 | m | 최대 왕복 보행거리 (walk-back) |
| `RESERVE` | 0.15 | 비율 | 복귀선 안전 예비분 |
| `O2SCALE` | 0.80 | 없음 | 산소 소모율 스케일. 복귀 완료 시 약 15% 가 남도록 맞춘 값이고 복귀선 로직에는 영향이 없음 |
| `SLOPE_BLOCK` | 25 | ° | A* 통행 불가 경사 |
| `ROCK_PENALTY` | 2.0 | 없음 | A* 간선비용 암석 가중. 비용 ×(1+ROCK_PENALTY·rock). rock=1 이면 ×3, rock=0 이면 ×1 |
| `MARS_R` | 3396190 | m | 화성 반지름 |
| `SCORE_RADIUS_M` | 800 | m | 핀 점수 조회 반경 (밖이면 폴백) |
| 틱 주기 | 120 | ms | `setInterval(step,120)` |
| `BASE` | `[18.44, 77.45]` | [lat,lon] | 기지 (착륙지) |

초기 설계의 `HR_REST=70` 상수는 데모 코드에 없음. 심박은 `HR_A`, `HR_B` 로 계산함.

---

## 5. 모델 함수 (실제 시그니처, 입출력, 단위)

### 5.1 대사, 소모품

```js
pandolf(L, v, G) → W            // 대사율 (와트)
//  L=적재 하중(kg), v=속도(m/s, 데모는 1.0), G=경사율(%) = tan(slope°)*100
//  = 1.5*M + 2*(M+L)*(L/M)² + ETA*(M+L)*(1.5*v² + 0.35*v*G*GMARS)

metabWeight(slope_deg, load) → ratio ≥ 1   // = pandolf(load,1.0,G)/pandolf(load,1.0,0), 평지=1
```

틱당 소모 (step 내부, 한 틱은 120 ms):

```
burn = pandolf(load, 1.0, returning?0:G) * O2W          // 산소 소모율 (L/min 상당)
o2  -= burn * 3 * O2SCALE        (하한 0)                 // 산소 감소 (복귀 중에는 G=0 으로 계산)
pct  = burn / VO2ABS                                     // 작업 강도 0~1+
hr   = min(round(HR_A + HR_B*pct), HRMAX)                // bpm
shF  = (발밑 칸 comm=='shadow') ? 1 - SHIELD : 1.0       // SHIELD = spe.shield_max_pct/100, 기본 0.20
dose += (RAD_DAY/1440) * 3 * shF                         // mSv 누적 (분당 RAD_DAY/1440)
SPE 활성 구간(onset_tick ≤ ticks < onset_tick+duration_ticks): dose += spike_mSv * shF
stam += pct>SUSTAIN ? -14*(pct-SUSTAIN) : +8*(SUSTAIN-pct)   // 체력, 0~100 범위로 제한
```

### 5.2 복귀선 (walk-back), 매 틱 재계산

```
rangeLeft = MAXWB * (o2/TANK)                    // 남은 산소로 갈 수 있는 총거리 (m)
radius    = max(0, round((rangeLeft - MAXWB*RESERVE) / 2))   // 복귀선 반경 (m) = (가용 − 예비) ÷ 왕복
```

지도의 `ring` 반경임. 산소가 줄면 반경이 줄어 먼 고득점 지점이 잠김.

### 5.3 거리

```js
metersBetween(a, b) → m     // a, b = {lat,lon} 객체
marsDist(a, b) → m          // a, b = [lat,lon] 배열 (Leaflet map.distance 대체)
```

### 5.4 생명점수 조회 (프론트는 격자를 읽기만 함)

```js
spotScore(spot) → { val:int(0~100), src:'격자(실데이터)'|'추정' }
//  cells 중 score!=null 인 최근접 칸 탐색. 거리 ≤ SCORE_RADIUS_M(800m) 이면 격자값(반올림),
//  아니면 spot.score(고정 추정값) 폴백.
cellAt(lat, lon) → {lat,lon,slope,comm,score,rock} | null   // 발밑: 유클리드 최근접 칸 (cells[] 는 rock 포함)
```

> score 계산은 프론트에 없음. `scripts/build_grid.py` 가 전처리 때 §6 공식으로 계산해 grid.geojson 에 넣어 둠. 프론트는 읽기만 함.

### 5.5 경로 탐색 (A*, 격자 그래프)

```js
buildGraph() → { nodes:[{lat,lon,slope,rock,x,y,nbrs:[{j,d}]}], step }   // 1회 생성, 캐시
//  투영: x=lon*kx, y=lat*ky (kx=cos(18.44°)*DEGLAT_M). step=최근접 이웃 거리의 중앙값.
//  이웃 = 거리 ≤ 1.6*step (8이웃, 대각 포함).
nearestNode(lat, lon) → index
astar(startIdx, goalIdx, load) → [nodeIdx…] | null
//  이진힙. 간선비용 = 거리(m) * metabWeight(이웃 slope, load) * (1 + ROCK_PENALTY*(이웃 rock||0)).
//  급경사와 바위밭일수록 비용이 커져 우회함. slope>25° 노드는 진입 금지. 휴리스틱은 직선 거리(비용 ≥ 거리라 admissible 유지).
computePath(target{lat,lon}, load) → (부수효과)  // PATH[[lat,lon]…], PATHcum[m], PATHlen(m), reachable(bool) 갱신 + pathLine 그림
//  격자 없음 → reachable=true + 직선 폴백. 목적지 칸 > 25° 또는 막힘 → reachable=false, 직선 폴백.
posAlongPath(d_m) → [lat,lon]    // 경로를 따라 d 미터 지점 보간
```

### 5.6 틱, 제어

```js
step()           // 타이머 콜백(120ms). target 이 없으면 아무 일도 하지 않음.
stop()           // clearInterval
// go:    done 이면 구간 리셋 → computePath → setInterval(step,120)
// reset: 전 상태 초기화(o2=TANK, stam=100, dose=0, walked=0, done=false), 마커 복귀
// setTarget(name): target 설정 + walked/returning/done/ticks 리셋 + computePath + 상태 표시
```

상태 라벨 우선순위(step 내): 산소 고갈(o2≤0) → 복귀 중(returning) → 복귀선 도달(walked≥radius) → 복귀선 근접(>0.8·radius) → 전진 여유. 그 뒤 경로가 막혔으면 도달 불가(직선 폴백), SPE 활성 구간이면 방사능 폭풍, `done` 이면 복귀 완료 순으로 덮어씀.

---

## 6. 생명점수 공식 (build_grid.py, 참고)

```
score(cell) = Σ(wᵢ·Sᵢ, 투입된 i) / Σ(wᵢ, 투입된 i) / 4 × 100      # 가용 지표만 재정규화
```

- 현재 투입 지표는 S1, S2 뿐이라 분모는 w_S1 + w_S2 = 0.457 + 0.257 = 0.714 임. S3, S4, S5 는 null 이라 포함되지 않음. S1 이 null 인 칸은 S2 만으로 계산함.
- `rock` 은 score 에 들어가지 않음. 안전, 이동 레이어(A* 우회, 게이트)로만 씀. 생명점수 지표(Sᵢ)와 구분해야 함.
- 지표가 하나도 없으면 `score=null` 임. 이 격자는 전 칸에 S2 가 있어 null 이 없음. 범위 25~100.
- 가중치는 `_meta.weights` (= weights.json 의 w_roc). 상세는 `docs/7_biosignature_design.md`.

---

## 7. 프론트 연결 가이드 (React + Leaflet + Recharts + Zustand)

### 7.1 Zustand store (제안 형태)

```ts
interface EvaState {
  // 정적 (로드 1회)
  grid: FeatureCollection; cells: Cell[]; graph: Graph;
  spots: Spot[]; consts: typeof MODEL_CONSTS;
  // 세션
  target: Spot|null; load: number;            // load = 적재 kg (0~50)
  path: LatLng[]; pathLen: number; reachable: boolean;
  // 틱 상태
  o2: number; stam: number; dose: number; walked: number;
  returning: boolean; done: boolean; running: boolean;
  // 파생 (selector): o2pct=o2/TANK*100, radius, hr, pct, status
  tick(): void; setTarget(name:string): void; go(): void; reset(): void;
}
```

- 틱은 store 액션 `tick()` 으로 옮기고 `useEffect` 에서 `setInterval(tick,120)` 을 검. 상태는 전부 store 에 두고 렌더는 selector 구독으로 함.
- `MODEL_CONSTS` 는 §4 값을 그대로 넣거나 `data/*.json` 에서 로드함. crew_spec, radiation, consumables 와 일부 겹치므로 단일 출처로 통일하는 편이 좋음.

### 7.2 Leaflet

- `<MapContainer center={[18.44,77.45]} zoom={14}>`. 타일은 OpenPlanetary Mars basemap (데모 HTML 의 `L.tileLayer` URL), `maxZoom:14`.
- `grid.geojson` → `<GeoJSON data={grid} style={slopeStyle}>` (경사 색은 §7.3 slopeColor) + 음영 필터 레이어.
- 대원 마커, 복귀선 `<Circle radius={radius}>`, 경로 `<Polyline positions={path} dashArray="6 4" color="#0ff">`.
- 좌표 순서: GeoJSON 의 `[lon,lat]` 는 react-leaflet 의 GeoJSON 컴포넌트가 내부에서 처리하므로 그대로 넘김. BASE, SPOTS, PATH 를 직접 쓸 때는 `[lat,lon]` 임.

### 7.3 slopeColor, rockColor (실제 임계)

```js
slopeColor: s>25:'#ff1111' · >15:'#ff5a00' · >8:'#ffd400' · >3:'#3fa019' · else:'#0a5a1e'
rockColor:  (v==null||v<0.1):투명 · >=0.6:'#5a2d0c' · >=0.4:'#8a4b1a' · >=0.25:'#b0712c' · else:'#d2a877'  (fillOpacity .6)
```

- 지도 레이어 토글은 3종임: `경사(실데이터)`, `암석(열관성)`, `교신 음영`. 암석 레이어는 THEMIS TI 에서 만든 rock 을 갈색 농도로 표시함.

### 7.4 Recharts

- 심박, 산소 소모율 시계열: `synthetic_eva.json` 의 `scenario`.
- 소모품과 지속시간 곡선: `consumables.json` 의 `duration_vs_workload`.
- 복귀선, 산소 실시간: store 의 `o2pct`, `radius`, `dose` 를 타임스탬프별로 누적해 선으로 그림.

---

## 8. 미구현, 주의 사항

- `S3`, `S4`, `S5` 는 항상 null 임. 차트나 점수에서 숫자로 가정하지 않음. S3, S4 는 설계 완료 미적용, S5 는 미투입임(`docs/9_verification_status.md`).
- `comm` 은 지형 시선 판정이고 측정한 전파 세기가 아님. 중계 위성은 반영하지 않음.
- 거리 `speed*3*2`, `burn*3`, 선량의 `*3` 에 들어 있는 `*3`, `*2` 는 데모 가속 스케일임. 실시간 EVA 가 아니므로 실제 시간축이 필요하면 다시 맞춰야 함.
- SPE 는 활성 구간 동안 틱마다 `spike_mSv·shF` 를 더하는 단순화 방식임. 실제 선량률 곡선이 아님.
- 피폭의 고도 보정 `altF` 와 다중 소모품 복귀 한계는 데모에 없음(`docs/1_model_spec_handoff.md` §6, §10).
- `consumables[].capacity` 는 단위가 붙은 문자열임. `spots[].score` 는 폴백값이고 런타임에 격자값으로 대체됨.
- 데모의 Leaflet 은 CDN(unpkg)에서 버전 고정 없이 불러옴.

---

## 9. 파일 목록 (프론트가 fetch 할 것)

| 파일 | 크기 | 포맷 | 역할 |
|---|---|---|---|
| `grid.geojson` | 약 1.0 MB | GeoJSON FC (3067) | 격자, 경사, 교신, Sᵢ, score, rock |
| `grid.js` | 약 1.0 MB | `window.GRID=FC` | 같은 데이터의 전역 변수판 (스크립트 로드용) |
| `data/spots.json` | 약 1.3 KB | JSON[] | 지점 4개 |
| `data/crew_spec.json` | 약 0.6 KB | JSON | 대원, 생리 상수 |
| `data/consumables.json` | 약 1.3 KB | JSON | 소모품, 지속시간 곡선 |
| `data/radiation.json` | 약 0.7 KB | JSON | 피폭 상수 |
| `data/synthetic_eva.json` | 약 1.4 KB | JSON | Recharts 시계열 6점 |
| `data/weights.json` | 약 4.0 KB | JSON | 지표, ROC/RS, 프리셋 |
| `data/layers.json` | 약 6.0 KB | JSON | 레이어, 게이트 정의 |
| `data/equipment.json` | 약 1.9 KB | JSON | 적재 하중 L |
| `data/donki_sample.json` | 약 1.0 KB | JSON | 우주기상 샘플, SPE 구간 |

---

## 10. 코드 대조 결과 (이 문서와 실제 파일)

문서 내용을 실제 파일과 대조한 결과임. `grid.geojson` 3,067칸 집계는 스크립트로, 상수는 `marswalk_grid_demo.html` 을 직접 대조함.

grid.geojson (스크립트 집계와 일치)

| 문서 내용 | 실제 값 | 결과 |
|---|---|---|
| features 3067, Polygon, 링 5점 | 3067 / Polygon / [5] | 일치 |
| slope_deg float, null 0, 0.5~22.7 | null 0, range [0.5, 22.7] | 일치 |
| comm clear/shadow, null 0 | {clear, shadow}, null 0 | 일치 |
| S1 int, null 579, 값 {1,3,4} | null 579, vals [1,3,4] | 일치 |
| S2 float, null 0, 0.2~4.0 | null 0, range [0.2, 4.0] | 일치 |
| S3, S4, S5 전부 null | 각 3067/3067 null | 일치 |
| score float, null 0, 25~100 | null 0, range [25.0, 100.0] | 일치 |
| rock float, null 0, 0~1 (이 격자 0.0~0.32) | null 0, range [0.0, 0.32] | 일치 |
| _meta.weights S4=.157 / S3=.09 | 동일 | 일치 |
| _meta.base=[77.45,18.44] [lon,lat] | 동일 | 일치 |
| _meta.rock_note 존재 | 존재 | 일치 |

상수 (marswalk_grid_demo.html 의 선언과 대조)

| 상수 | 문서 | 코드 선언 | 결과 |
|---|---|---|---|
| MARS_R | 3396190 | `const MARS_R=3396190` | 일치 |
| MAXWB | 2000 | `MAXWB=2000` | 일치 |
| RESERVE | 0.15 | `RESERVE=0.15` | 일치 |
| O2SCALE | 0.80 | `O2SCALE=0.80` | 일치 |
| TANK | 500 | `TANK=500` | 일치 |
| ETA / GMARS / O2W | 2.0 / 0.38 / 1/348 | `ETA=2.0,GMARS=0.38,O2W=1/348` | 일치 |
| M / VO2ABS / SUSTAIN | 80 / 3.0 / 0.35 | `M=80,VO2ABS=3.0, … SUSTAIN=0.35` | 일치 |
| HR_A / HR_B / HRMAX | 70.5 / 113.2 / 186 | `HR_A=70.5,HR_B=113.2,HRMAX=186` | 일치 |
| RAD_DAY | 0.64 | `RAD_DAY=0.64` | 일치 |
| SLOPE_BLOCK | 25 | `const SLOPE_BLOCK=25` | 일치 |
| ROCK_PENALTY | 2.0 | `const ROCK_PENALTY=2.0` | 일치 |
| SCORE_RADIUS_M | 800 | `SCORE_RADIUS_M=800` | 일치 |
| 틱 120 ms | 120 | `setInterval(step,120)` | 일치 |
| BASE [18.44, 77.45] | [lat,lon] | `const BASE=[18.44,77.45]` | 일치 |

이전 판 문서는 심박을 `HR_REST=70` 과 `(HRMAX−HR_REST)·pct` 로, 선량을 차폐 없는 식으로 적고 있었음. 코드와 달라 `HR_A`, `HR_B` 식과 `shF`, SPE 가산이 들어간 식으로 고침.

함수 시그니처 (직접 대조): pandolf(L,v,G), metabWeight(slope,load), marsDist([lat,lon]), buildGraph(nodes 에 rock 포함), astar(간선비용 ×(1+2·rock)), computePath, posAlongPath, spotScore, cellAt, step, stop 모두 일치.

rock 바위밭 우회 (브라우저에서 확인한 기록값): 같은 그래프에서 rock 을 반영한 A* 와 반영하지 않은 A* 를 비교함(load=20). 이번 정리에서는 다시 실행하지 않았음.

| 목적지 | 반영 평균 rock | 미반영 평균 rock | 반영 최대 rock | 미반영 최대 rock | 경로 차이 |
|---|---|---|---|---|---|
| 델타 전선 | 0.174 | 0.174 | 0.24 | 0.24 | 동일 (이미 최소) |
| Cheyava | 0.147 | 0.153 | 0.26 | 0.31 | 우회 (0.31 칸 회피) |
| Hawksbill | 0.195 | 0.195 | 0.24 | 0.24 | 동일 |
| Séítah | 0.201 | 0.203 | 0.28 | 0.28 | 우회 |

바위가 많은 칸이 최단 경로 위에 있을 때 rock 이 더 낮은 쪽으로 경로가 바뀜(네 경우 모두 반영 ≤ 미반영). 이 5km 클립 영역은 전반적으로 모래(최대 rock 0.32)라 효과는 작음.

data/*.json 필드: §3 표의 필드, 타입, 단위는 각 파일 원본과 대조함(crew_spec, consumables, radiation, synthetic_eva, weights, layers, spots, equipment, donki).

아래는 코드 그대로 계약에 적어 둔 특이점이고 버그가 아님.

1. `_meta.base` 와 geometry 는 `[lon,lat]` 인데 앱 `BASE` 는 `[lat,lon]` 임. §1 규약으로 구분함.
2. `spots.json` 의 `score` (92, 85, 78, 54)는 격자의 런타임 값과 다름. 폴백 설계임(§5.4).
3. `S1` 관측값에 2 가 없음. `build_grid.py` 의 CRISM 범례 룩업이 1, 3, 4 만 부여하기 때문임. 스키마 범위는 0~4 로 둠.

---

## 11. 관련 문서

- `docs/1_model_spec_handoff.md` 모델 공식, 상수
- `docs/7_biosignature_design.md` 점수 설계
- `docs/8_grid_guide.md` 격자 전처리
- `docs/9_verification_status.md` 검증 현황
- `docs/2_sources.md` 출처
