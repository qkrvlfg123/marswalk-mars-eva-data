# MARSWALK — 데이터·API 계약서 (Data & API Spec) (2026-11-15)

> **목적:** 프론트 개발자가 **이 문서만 보고** React + Leaflet + Recharts + Zustand로 데모를 재구현할 수 있게 하는 계약서.
> **원칙:** 전부 실제 산출 파일(`grid.geojson`, `data/*.json`, `marswalk_grid_demo.html`)에서 읽어 기록. 추측 없음. (문서 끝 §10에 코드 대조 검증.)
> **좌표 규약은 §1에서 반드시 먼저 확인** — GeoJSON은 `[lon,lat]`, 앱 내부(Leaflet·BASE·SPOTS·경로)는 `[lat,lon]`. 섞이면 지도가 뒤집힌다.

---

## 0. 런타임 흐름 (fetch → store → tick → render)

```
① 로드    fetch('grid.geojson')  →  { type:'FeatureCollection', _meta, features[3067] }
          fetch('data/*.json')   →  상수·스펙·지점
② 파생    features → cells[]  (셀 중심 centroid + slope/comm/score)   ← 발밑 조회·A* 노드
          features → graph   (buildGraph: 투영 좌표 + 8이웃 인접리스트)  ← 1회 캐시
③ 선택    setTarget(spot)    →  computePath(target, load)  →  PATH[], PATHlen, reachable
④ 틱      setInterval(step, 120ms)  →  walked 누적 → 위치/소모품/경사/상태 갱신
⑤ 렌더    store 구독 → 패널(산소·체력·피폭·심박) + 지도(대원 마커·복귀선 ring·경로 polyline)
```

- **틱 주기 = 120 ms.** 한 틱에 `walked`(기지로부터 경로 이동거리, m)가 **±6 m** 변함(전진 +, 복귀 −). → 재생 속도는 실제 EVA 시간이 아닌 **데모 가속 스케일**(아래 상수 `speed*3*2`).
- **복귀 트리거:** `walked ≥ min(목표거리, 복귀선반경)` 이면 `returning=true`. `walked ≤ 0` 이고 산소가 출발 대비 줄었으면 → EVA 종료(`done=true`, 타이머 정지).
- **격자 없을 때 폴백:** `window.GRID`(= grid.geojson 내용)가 없으면 경사는 수동 슬라이더, 경로는 직선 보간. 앱은 그래도 동작해야 함.

---

## 1. 좌표·단위 규약 (⚠️ 계약의 핵심)

| 맥락 | 순서 | 예 | 비고 |
|---|---|---|---|
| **grid.geojson geometry** | `[lon, lat]` | `[77.4323, 18.5240]` | GeoJSON 표준(RFC 7946) |
| **앱 내부 좌표**(BASE·SPOTS·PATH·Leaflet) | `[lat, lon]` | `[18.44, 77.45]` | Leaflet `LatLng` 관례 |
| 각도 | WGS식 십진도(deg) | lon 77.4, lat 18.4 | Jezero(화성) |
| 거리 | **미터(화성 반지름 기준)** | — | 지구 반지름 금지, §4 `marsDist` 사용 |
| 경사 `slope_deg` | 도(°) | 0.5~22.7 | |
| 생명점수 `score` | 0~100 | 25~100 | |

- **화성 거리 상수:** `MARS_R = 3396190 m` (USGS 3396.19 km). `DEGLAT_M = MARS_R·π/180 ≈ 59,276 m/°`.
- **거리식(등장방형 근사, 고정 위도):** `kx = cos(18.44°)·DEGLAT_M`, `dist = hypot((Δlon)·kx, (Δlat)·DEGLAT_M)`. 위도 18.44°를 상수로 고정(셀별 cos 재계산 안 함) — Jezero 국소 영역이라 오차 무시 가능. **Leaflet `map.distance()`는 지구 반지름이라 쓰지 말 것**(≈1.88배 과대).

---

## 2. `grid.geojson` 계약 (메인 데이터)

- 최상위: `{ "type": "FeatureCollection", "_meta": {…}, "features": [3067] }`
- 각 feature: `{ "type":"Feature", "properties":{…}, "geometry":{…} }`
- geometry: **Polygon**, 링 1개, 점 5개(사각 셀, 첫 점=마지막 점 닫힘). 셀 크기 ≈ **160 m**.

### 2.1 `properties` 스키마 (전 3067칸 실측 집계)

| 필드 | 타입 | 단위/범위 | null | 의미 |
|---|---|---|---|---|
| `slope_deg` | number(float) | 0.5 ~ 22.7 ° | **없음**(0/3067) | DEM 경사. 안전 게이트(>25° 통행불가; 실데이터엔 25 초과 없음) |
| `comm` | string | `"clear"` \| `"shadow"` | **없음** | 기지→셀 가시선 교신. shadow=음영. (clear 2483 / shadow 584) |
| `S1` | number(int) | 1 ~ 4 (관측값 {1,3,4}) | **579칸 null** | 함수/점토광물 지표. CRISM. null=미식별(검정)·배경(흰색) |
| `S2` | number(float) | 0.2 ~ 4.0 | 없음 | 퇴적·델타 지표. SIM3464. 칸 footprint 평균이라 소수 |
| `S3` | null | — | **전부 null** | 보존성 염류. 설계완료·비적용(Jezero 희박) — [[9_verification_status]] |
| `S4` | null | — | **전부 null** | 물 활동. 설계완료·비적용(S1·S2에 내재) |
| `S5` | null | — | **전부 null** | 로버 근접. 미투입 |
| `score` | number(float) | 25.0 ~ 100.0 | 없음 | 생명점수(가용지표 재정규화, §6). 전 칸 채움 |
| `rock` | number(float) | 0.0 ~ 1.0 (본 격자 관측 0.0~0.32) | TI 무효 칸만(본 격자 null 0) | **암석 피복**(THEMIS 열관성→rock). 안전레이어(점수 아님)·A* 바위밭 우회. 0=먼지/모래, 1=바위/화성암 |

> **프론트 주의:** `Sᵢ`는 **null 가능**(S1) 또는 **항상 null**(S3·S4·S5). 숫자 가정 금지 — `v == null ? '—' : v`. `score`·`rock`은 본 격자에선 항상 숫자지만 `rock`도 일반적으로 null 가능(TI=0 nodata).

### 2.2 `_meta` (실제 내용)

```json
{
  "cell_m": 160,
  "base": [77.45, 18.44],            // [lon, lat] — Perseverance 착륙지
  "note": "slope·comm=DEM 실데이터 / Sᵢ=래스터 준 것만(없으면 null)",
  "score_note": "score=가용지표 재정규화, 현재 S1(CRISM 점토·탄산염)+S2(SIM3464 퇴적·델타) 기반",
  "rock_note": "rock=THEMIS 열관성(Zenodo 4931348, Edwards&Buz 2021)→암석피복 0~1. 안전레이어(점수 아님), A* 간선비용·바위밭 우회",
  "weights": { "S1":0.457, "S2":0.257, "S4":0.157, "S3":0.09, "S5":0.04 }
}
```

- `_meta.base`는 `[lon,lat]` 순서임에 주의(geometry와 동일 규약). 앱 `BASE`는 `[lat,lon]=[18.44,77.45]`.
- `_meta.weights`: **S4=0.157(순위3, 물 활동), S3=0.09(순위4, 염류)** — 번호≠순위(ROC는 순위로 가중치 결정). score 계산에 쓰는 가중치 기준값.

---

## 3. `data/*.json` 계약 (상수·스펙·지점)

### 3.1 `spots.json` — 탐사 지점 (배열) / `spots.js` — 동일 데이터의 `window.SPOTS` 전역판

| 필드 | 타입 | 단위 | 의미 |
|---|---|---|---|
| `name` | string | — | 지점명(목적지 식별 키) |
| `lat` | number | deg | 위도 |
| `lon` | number | deg | 경도 |
| `score` | number | 0~100 | **폴백/초기 추정값.** 실제는 런타임에 격자 최근접칸 score로 덮임(§5 `spotScore`) |
| `note` | string | — | 설명 |
| `img` | string(URL) | — | Perseverance raw 실사 URL(mars.nasa.gov) |

4개 지점: 델타 전선·Cheyava 방향·Hawksbill Gap·Séítah. (`spots.js`는 `const SPOTS=[…]`로 노출 — HTML 인라인판과 동일)

### 3.2 `crew_spec.json` — 대원 제원

| 경로 | 값 | 단위 | 의미 |
|---|---|---|---|
| `age.value` | 34 | yr | 나이(HRmax용) |
| `weight_kg.value` | 80 | kg | 체중 = Pandolf `M` |
| `vo2peak.value` | 37.5 | ml/kg/min | 최대산소섭취 |
| `sustainable_pct.value` | 0.35 | 비율 | 지속가능 작업률 = `SUSTAIN` |
| `hr_model.formula` | `"HR = 70.5 + 113.2*pctVO2"` | — | PhysioNet 보정(R²=0.77) |
| `hrmax.value` | 186 | bpm | `220-age` |

### 3.3 `consumables.json` — EVA 소모품

| 경로 | 값 | 의미 |
|---|---|---|
| `nominal_duration_min` | 480 | 공칭 지속(분) |
| `nominal_metabolic_BTU_hr` | 930 | 공칭 대사율 |
| `duration_vs_workload[]` | `{BTU_hr, hours}` ×3 | 대사율↔지속시간 곡선(930/8h, 1200/6h, 1600/5h) |
| `consumables[]` | `{key,name,capacity,scales_with_metabolic,source}` | o2/fw/co/ba 4종. `capacity`는 **문자열**(단위 포함, 예 `"1430 psi"`) |

> 주의: `capacity`는 숫자가 아니라 단위 포함 문자열. 파싱 필요. `scales_with_metabolic`만 boolean.

### 3.4 `radiation.json` — 피폭 상수

| 경로 | 값 | 단위 | 의미 |
|---|---|---|---|
| `baseline_mSv_per_day` | 0.64 | mSv/day | 기준 선량 = `RAD_DAY` |
| `spe_spike_mSv` | `[1.2, 19.5]` | mSv | SPE 스파이크 범위 |
| `terrain_shielding_max_pct` | 20 | % | 지형 차폐 최대 |
| `xray_equiv_mSv` | 0.1 | mSv | 흉부 X선 1장 환산 |
| `donki_api` | URL | — | 우주기상 라이브 |

### 3.5 `synthetic_eva.json` — Recharts용 시계열 ⭐

`scenario[]` 각 원소 = 한 시점:

| 필드 | 타입 | 단위 |
|---|---|---|
| `t_min` | int | 분(0,10,…,50) |
| `slope_deg` | number | ° |
| `load_kg` | number | kg |
| `pctVO2` | number | 0~1+ (1 초과=지속불가) |
| `HR_bpm` | int | bpm |
| `O2_Lmin` | number | L/min |
| `sustainable` | boolean | pctVO2≤1 여부 |

→ **Recharts `<LineChart data={scenario}>`** 에 그대로 투입(x=`t_min`, y=`HR_bpm`/`O2_Lmin`/`pctVO2`).

### 3.6 `weights.json` — 생명점수 가중치/지표 정의

- `indicators[]`: `{key, rank, name, layer, why, src, w_roc, w_rs}`. key=S1·S2·S4·S3·S5, rank=1~5.
- **rank 3 = S4(물 활동, w_roc 0.157), rank 4 = S3(염류, w_roc 0.09)** — grid `_meta.weights`와 일치.
- `presets_rank`: 순위 재배열 프리셋 3종(과학권장/물추적/검증우선). UI는 숫자 입력이 아니라 **순위 드래그**로 재계산.

### 3.7 `layers.json` — 지도 레이어 정의

- `science_layers.items[]`(S1·S2·S4·S3·S5 각 `{feeds,name,product,source,rubric}`) + `safety_layers.items[]`(walkback/slope/**rock**/rad/comm `{key,name,product,source,gate}`).
- `rock` 안전레이어 = THEMIS 열관성(Zenodo 4931348)→grid `rock` 필드. gate=SOFT(A* 비용 ×(1+2·rock) 우회), 점수엔 미합산. → 지도 '5종 레이어'의 **열(thermal)** 충족.
- 안전 레이어는 **점수에 합산 금지, 게이트 전용**. `_combine`: `recommend = gate_hard ? 0 : score × soft_penalty`.

### 3.8 `donki_sample.json` — 우주기상 리플레이 샘플

- `event{messageType:"FLR", messageIssueTime, note}`. 실 운용은 DONKI 라이브.

### 3.9 `equipment.json` — 적재 하중 L 마스터

- `items[]`: `{name, kg, src}`(HTC 13.4·ALSRC 6.7 등, Apollo 실측). `apollo_tool_totals_kg`(임무별 22.9~53.0). `plss_kg.value` 47. `_default_L_kg` 20. → Pandolf `L` 입력 근거. 상세 [[2_sources]].

---

## 4. 모델 상수 (marswalk_grid_demo.html — 실제 값)

| 상수 | 값 | 단위 | 의미 |
|---|---|---|---|
| `M` | 80 | kg | 체중(Pandolf 기준 질량) |
| `VO2ABS` | 3.0 | L/min | 절대 최대 산소섭취(pct 분모) |
| `ETA`(η) | 2.0 | — | 지형계수(레골리스≈모래) |
| `GMARS` | 0.38 | — | 화성 중력비 |
| `O2W` | 1/348 | (L/min)/W | 대사율(W)→산소율 환산 |
| `SUSTAIN` | 0.35 | — | 지속가능 작업률 임계 |
| `HR_REST` | 70 | bpm | 안정 심박 |
| `HRMAX` | 186 | bpm | 최대 심박 |
| `TANK` | 500 | (추상단위) | 산소 탱크 용량(=100%) |
| `RAD_DAY` | 0.64 | mSv/day | 일일 피폭 기준 |
| `MAXWB` | 2000 | m | 최대 왕복 복귀거리(walk-back) |
| `RESERVE` | 0.15 | 비율 | 복귀선 안전 예비분 |
| `O2SCALE` | 0.80 | — | 산소 소모율 스케일(복귀 완료 시 ~15% 잔량 되게 튜닝. **복귀선 로직엔 무영향**) |
| `SLOPE_BLOCK` | 25 | ° | A* 통행불가 경사 |
| `ROCK_PENALTY` | 2.0 | — | A* 간선비용 암석 가중. 비용 ×(1+ROCK_PENALTY·rock). rock=1→×3, rock=0→×1 |
| `MARS_R` | 3396190 | m | 화성 반지름 |
| `SCORE_RADIUS_M` | 800 | m | 핀 점수 조회 반경(밖이면 폴백) |
| 틱 주기 | 120 | ms | `setInterval(step,120)` |
| `BASE` | `[18.44, 77.45]` | [lat,lon] | 기지(착륙지) |

---

## 5. 모델 함수 (실제 시그니처 · 입출력 · 단위)

### 5.1 대사·소모품

```js
pandolf(L, v, G) → W            // 대사율(와트)
//  L=적재하중(kg), v=속도(m/s, 데모는 1.0), G=경사율(%) = tan(slope°)*100
//  = 1.5*M + 2*(M+L)*(L/M)² + ETA*(M+L)*(1.5*v² + 0.35*v*G*GMARS)

metabWeight(slope_deg, load) → ratio ≥ 1   // = pandolf(load,1.0,G)/pandolf(load,1.0,0), 평지=1
```

**틱당 소모(step 내부, 각 틱=120ms):**
```
burn = pandolf(load, 1.0, returning?0:G) * O2W          // 산소율(L/min 상당)
o2  -= burn * 3 * O2SCALE        (하한 0)                 // 산소 감소(복귀 중엔 G=0으로 계산)
pct  = burn / VO2ABS                                     // 작업강도 0~1+
hr   = min(round(HR_REST + (HRMAX-HR_REST)*pct), HRMAX)  // bpm
dose += (RAD_DAY/1440) * 3                               // mSv 누적 (분당=RAD_DAY/1440)
stam += pct>SUSTAIN ? -14*(pct-SUSTAIN) : +8*(SUSTAIN-pct)   // 체력 0~100 clamp
```

### 5.2 복귀선(walk-back) — 매 틱 재계산

```
rangeLeft = MAXWB * (o2/TANK)                    // 남은 산소로 갈 수 있는 총거리(m)
radius    = max(0, round((rangeLeft - MAXWB*RESERVE) / 2))   // 복귀선 반경(m) = (가용-예비)÷왕복
```
→ 지도의 `ring` 반경. 산소 줄면 반경 수축 → 먼 고득점 지점 자동 잠김.

### 5.3 거리

```js
metersBetween(a, b) → m     // a,b = {lat,lon} 객체
marsDist(a, b) → m          // a,b = [lat,lon] 배열 (Leaflet map.distance 대체)
```

### 5.4 생명점수 조회 (프론트는 격자를 읽기만)

```js
spotScore(spot) → { val:int(0~100), src:'격자(실데이터)'|'추정' }
//  cells 중 score!=null 최근접칸 탐색. 거리 ≤ SCORE_RADIUS_M(800m)면 격자값(반올림),
//  아니면 spot.score(하드코딩 추정) 폴백.
cellAt(lat, lon) → {lat,lon,slope,comm,score,rock} | null   // 발밑: 유클리드 최근접 셀 (cells[]는 rock 포함)
```
> **score 계산 자체는 프론트에 없음.** `build_grid.py`(파이썬)가 전처리 때 §6 공식으로 산출해 grid.geojson에 박아둠. 프론트는 읽기 전용.

### 5.5 경로탐색 (A*, 격자 그래프)

```js
buildGraph() → { nodes:[{lat,lon,slope,rock,x,y,nbrs:[{j,d}]}], step }   // 1회 생성·캐시
//  투영: x=lon*kx, y=lat*ky (kx=cos(18.44°)*DEGLAT_M). step=최근접이웃거리 중앙값.
//  이웃 = 거리 ≤ 1.6*step (8이웃, 대각 포함).
nearestNode(lat, lon) → index
astar(startIdx, goalIdx, load) → [nodeIdx…] | null
//  이진힙. 간선비용 = 거리(m) * metabWeight(이웃slope, load) * (1 + ROCK_PENALTY*(이웃rock||0)).
//  → 급경사·바위밭일수록 비용↑ → 우회. slope>25° 노드 진입 금지. 휴리스틱=직선 marsDist(비용≥거리라 admissible 유지).
computePath(target{lat,lon}, load) → (부수효과)  // PATH[[lat,lon]…], PATHcum[m], PATHlen(m), reachable(bool) 갱신 + pathLine 그림
//  격자 없음 → reachable=true + 직선 폴백. 목적지칸>25° 또는 막힘 → reachable=false, 직선 폴백.
posAlongPath(d_m) → [lat,lon]    // 경로 따라 d미터 지점 보간
```

### 5.6 틱/제어

```js
step()           // 타이머 콜백(120ms). target 없으면 no-op.
stop()           // clearInterval
// go:    done이면 구간 리셋 → computePath → setInterval(step,120)
// reset: 전 상태 초기화(o2=TANK, stam=100, dose=0, walked=0, done=false), 마커 복귀
// setTarget(name): target 설정 + walked/returning/done 리셋 + computePath + 상태표시
```

**상태 라벨 우선순위(step 내):** `산소 고갈(o2≤0)` → `복귀 중(returning)` → `복귀선 도달(walked≥radius)` → `복귀선 근접(>0.8·radius)` → `전진 여유` → (경로 막힘이면 `도달불가·직선폴백`) → (`done`이면 `✅ 복귀 완료`로 덮어씀).

---

## 6. 생명점수 공식 (build_grid.py, 참고)

```
score(cell) = Σ(wᵢ·Sᵢ, 투입된 i) / Σ(wᵢ, 투입된 i) / 4 × 100      # 가용 지표만 재정규화
```
- 현재 투입 = S1·S2만 → 분모 = w_S1+w_S2 = 0.457+0.257 = **0.714**. (S3·S4·S5=null → 미포함)
- **`rock`은 score에 들어가지 않음** — 안전/이동 레이어(A* 우회·게이트)로만 쓴다. 생명점수 지표(Sᵢ)와 혼동 금지.
- 하나도 없으면 `score=null`(관측상 전 칸 S2 있어 null 없음). 범위 25~100.
- 가중치는 `_meta.weights`(=weights.json의 w_roc). 상세 [[7_biosignature_design]].

---

## 7. 프론트 연결 가이드 (React + Leaflet + Recharts + Zustand)

### 7.1 Zustand store(제안 형태)
```ts
interface EvaState {
  // 정적(로드 1회)
  grid: FeatureCollection; cells: Cell[]; graph: Graph;
  spots: Spot[]; consts: typeof MODEL_CONSTS;
  // 세션
  target: Spot|null; load: number;            // load=적재 kg(0~50)
  path: LatLng[]; pathLen: number; reachable: boolean;
  // 틱 상태
  o2: number; stam: number; dose: number; walked: number;
  returning: boolean; done: boolean; running: boolean;
  // 파생(selector): o2pct=o2/TANK*100, radius, hr, pct, status
  tick(): void; setTarget(name:string): void; go(): void; reset(): void;
}
```
- **틱은 store 액션 `tick()`** 으로 옮기고 `useEffect`에서 `setInterval(tick,120)`. 상태는 전부 store에, 렌더는 selector 구독.
- `MODEL_CONSTS`는 §4 그대로 하드코딩하거나 `data/*.json`에서 로드(crew_spec·radiation·consumables와 일부 중복 — 단일 출처로 통일 권장).

### 7.2 Leaflet
- `<MapContainer center={[18.44,77.45]} zoom={14}>`. 타일 = OpenPlanetary Mars basemap(§HTML L.46 URL), `maxZoom:14`.
- `grid.geojson` → `<GeoJSON data={grid} style={slopeStyle}>`(경사 색 §slopeColor) + 음영 필터 레이어.
- 대원 마커·복귀선 `<Circle radius={radius}>`·경로 `<Polyline positions={path} dashArray="6 4" color="#0ff">`.
- **좌표 변환 필수:** GeoJSON `[lon,lat]`를 Leaflet에 직접 주면 됨(react-leaflet GeoJSON은 내부 처리). 단 BASE/SPOTS/PATH 직접 쓸 땐 `[lat,lon]`.

### 7.3 slopeColor / rockColor (실제 임계)
```js
slopeColor: s>25:'#ff1111' · >15:'#ff5a00' · >8:'#ffd400' · >3:'#3fa019' · else:'#0a5a1e'
rockColor:  (v==null||v<0.1):투명 · >=0.6:'#5a2d0c' · >=0.4:'#8a4b1a' · >=0.25:'#b0712c' · else:'#d2a877'  (fillOpacity .6)
```
- 지도 레이어 토글 3종: `경사(실데이터)` · `암석(열관성)` · `교신 음영`. 암석 레이어는 THEMIS TI→rock을 갈색 농도로.

### 7.4 Recharts
- 심박/산소율 시계열: `synthetic_eva.json.scenario`.
- 소모품↔지속곡선: `consumables.json.duration_vs_workload`.
- 복귀선/산소 실시간: store의 `o2pct`·`radius`·`dose`를 타임스탬프별로 누적해 라인.

---

## 8. 미구현/주의 (계약상 명확히)

- `S3·S4·S5`는 **항상 null** — 차트/점수에서 숫자 가정 금지. S3·S4는 설계완료·비적용, S5 미투입([[9_verification_status]]).
- `comm`은 **지형 가시선 판정**이지 측정 전파세기가 아님. 중계위성 미반영.
- 거리 `speed*3*2`, `burn*3`, `dose*3` 의 `*3`/`*2`는 **데모 가속 스케일** — 실시간 EVA 아님. 실제 시간축이 필요하면 재튜닝.
- `consumables[].capacity`는 단위 포함 **문자열**. `spots[].score`는 폴백값(런타임에 격자값으로 교체).

---

## 9. 파일 매니페스트 (프론트가 fetch할 것)

| 파일 | 크기 | 포맷 | 역할 |
|---|---|---|---|
| `grid.geojson` | ~1.0 MB | GeoJSON FC(3067) | 격자·경사·교신·Sᵢ·score·**rock** |
| `grid.js` | — | `window.GRID=FC` | 위와 동일 데이터의 전역 변수판(스크립트 로드용) |
| `data/spots.json` | ~1.2 KB | JSON[] | 지점 4 |
| `data/crew_spec.json` | ~0.6 KB | JSON | 대원·생리 상수 |
| `data/consumables.json` | ~1.3 KB | JSON | 소모품·지속곡선 |
| `data/radiation.json` | ~0.7 KB | JSON | 피폭 상수 |
| `data/synthetic_eva.json` | ~1.2 KB | JSON | Recharts 시계열 6점 |
| `data/weights.json` | ~3.9 KB | JSON | 지표·ROC/RS·프리셋 |
| `data/layers.json` | ~3.8 KB | JSON | 레이어·게이트 정의 |
| `data/equipment.json` | ~1.9 KB | JSON | 적재 하중 L |
| `data/donki_sample.json` | ~0.4 KB | JSON | 우주기상 샘플 |

---

## 10. ✅ 코드 대조 검증 (이 문서 ↔ 실제 파일)

문서 작성 후 실제 파일과 대조한 결과. (`grid.geojson` 3067칸 집계는 스크립트로, 상수는 `marswalk_grid_demo.html` 직접 대조.)

**grid.geojson (스크립트 집계와 일치)**
| 주장 | 실측 | 일치 |
|---|---|---|
| features 3067, Polygon, 링 5점 | 3067 / Polygon / [5] | ✅ |
| slope_deg float, null 0, 0.5~22.7 | null 0, range[0.5,22.7] | ✅ |
| comm clear/shadow, null 0 | {clear,shadow}, null 0 | ✅ |
| S1 int, null 579, 값 {1,3,4} 1~4 | null 579, vals[1,3,4] | ✅ |
| S2 float, null 0, 0.2~4.0 | null 0, range[0.2,4.0] | ✅ |
| S3·S4·S5 전부 null | 각 3067/3067 null | ✅ |
| score float, null 0, 25~100 | null 0, range[25.0,100.0] | ✅ |
| rock float, null 0, 0~1(본격자 0.0~0.32) | null 0, range[0.0,0.32] | ✅ |
| _meta.weights S4=.157/S3=.09 | 동일 | ✅ |
| _meta.base=[77.45,18.44] [lon,lat] | 동일 | ✅ |
| _meta.rock_note 존재 | 존재 | ✅ |

**상수 (marswalk_grid_demo.html 라인 대조)**
| 상수 | 문서 | 코드 | 일치 |
|---|---|---|---|
| MARS_R | 3396190 | L81 `=3396190` | ✅ |
| MAXWB | 2000 | L176 | ✅ |
| RESERVE | 0.15 | L176 | ✅ |
| O2SCALE | 0.80 | L176 | ✅ |
| TANK | 500 | L176 | ✅ |
| ETA/GMARS/O2W | 2.0/0.38/1/348 | L175 | ✅ |
| M/VO2ABS/SUSTAIN | 80/3.0/0.35 | L175 | ✅ |
| HR_REST/HRMAX | 70/186 | L175 | ✅ |
| RAD_DAY | 0.64 | L176 | ✅ |
| SLOPE_BLOCK | 25 | L80 | ✅ |
| ROCK_PENALTY | 2.0 | L81 | ✅ |
| SCORE_RADIUS_M | 800 | L155 | ✅ |
| 틱 120ms | 120 | L232 | ✅ |
| BASE [18.44,77.45] | [lat,lon] | L44 | ✅ |

**함수 시그니처 (직접 대조)** — pandolf(L,v,G) ✅ · metabWeight(slope,load) ✅ · marsDist([lat,lon]) ✅ · buildGraph(nodes에 rock 포함)/astar(간선비용 ×(1+2·rock))/computePath/posAlongPath ✅ · spotScore/cellAt ✅ · step/stop ✅.

**rock 바위밭 우회 (브라우저 검증)** — 동일 그래프에서 rock-aware A* vs rock-off A* 비교(load=20):
| 목적지 | aware 평균rock | off 평균rock | aware 최대rock | off 최대rock | 경로 달라짐 |
|---|---|---|---|---|---|
| 델타 전선 | 0.174 | 0.174 | 0.24 | 0.24 | 동일(이미 최소) |
| Cheyava | **0.147** | 0.153 | **0.26** | 0.31 | ✅ 우회(0.31칸 회피) |
| Hawksbill | 0.195 | 0.195 | 0.24 | 0.24 | 동일 |
| Séítah | **0.201** | 0.203 | 0.28 | 0.28 | ✅ 우회 |
→ 바위 많은 칸이 최단경로 위에 있을 때 더 낮은 rock으로 재경로(aware ≤ off 전 케이스). 본 5km 클립은 전역 모래(최대 rock 0.32)라 효과는 소폭이지만 방향은 정확.

**data/*.json 필드** — §3 표의 필드·타입·단위는 각 파일 원본과 1:1 대조 완료(crew_spec·consumables·radiation·synthetic_eva·weights·layers·spots·equipment·donki). ✅

> **불일치 0건.** 단, 아래는 "코드 그대로"라 계약에 명시한 의도된 특이점(버그 아님): ⓐ `_meta.base`·geometry는 `[lon,lat]`인데 앱 `BASE`는 `[lat,lon]` — §1 규약으로 분리. ⓑ `spots.json.score`(92/85/78/54)는 격자 런타임값과 다름 — 폴백 설계(§5.4). ⓒ `S1` 관측값에 `2`가 없음(루브릭엔 존재) — Jezero에 해당 광물 조합이 없어서일 뿐 스키마는 1~4.

---

## 11. 관련 문서
- [[1_model_spec_handoff]] 모델 공식·상수 · [[7_biosignature_design]] 점수 설계 · [[8_grid_guide]] 격자 전처리 · [[9_verification_status]] 검증 현황 · [[2_sources]] 출처
