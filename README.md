# MARSWALK, 화성 Jezero EVA 데이터

화성 Jezero 크레이터 도보 선외활동(EVA, Extra-Vehicular Activity)의 목적지 선정과 복귀 안전 판단에 쓰는 격자 데이터, 생체 모델 상수, 지도 데모를 공개 데이터로 만든 저장소임.

- 팀 team-navis 가 NASA Space Apps Challenge 2026 (Seoul) 에 낸 작업 중 데이터 파트임. 이 저장소 작성자가 데이터 수집, 정제, 격자 산출을 맡았음. 메인 3D 데모는 팀 저장소에 있고 이 저장소에는 없음.
- 표기 규칙: (코드) 는 이 저장소의 파일(`grid.geojson`, `data/*.json`, `scripts/*.py`, `marswalk_grid_demo.html`)에서 직접 확인하거나 다시 계산한 값임. (기록) 은 기존 문서에만 남아 있고 원본 데이터나 계산 파일이 저장소에 없어 다시 계산하지 못한 값임.
- 초기값: 공개 데이터나 문헌만으로 정한 기준값을 뜻함. 현장 검증을 거치지 않았음.
- 최신 갱신: 2026-11-15. 생명점수가 S1, S2 실데이터로 채워져 전 칸에 점수가 있음.

## 배경

도보 EVA 한 번에는 두 가지 판단이 동시에 필요함. 하나는 과학적으로 가치가 높은 목적지 선정이고, 다른 하나는 그 목적지까지 다녀올 수 있는지에 대한 안전 판단임. 이 저장소는 앞쪽을 생명점수(Biosignature Score) 격자로, 뒤쪽을 복귀선, 경사, 교신 음영, 피폭, 심박 모델로 나누어 각각 공개 데이터로 채움.

- 과학 점수와 안전은 섞지 않음. 안전 레이어는 점수에 더하지 않고 게이트와 경로 비용으로만 씀.
- 앱은 추천과 경고만 하고 최종 go/no-go 는 우주인이 판단하는 것으로 설계함.
- 땅 쪽 데이터와 사람 쪽 데이터는 한 체인으로 이어짐. 경사가 바뀌면 대사율과 산소 소모율이 바뀌고, 산소 잔량이 복귀 반경을 정하고, 복귀 반경이 갈 수 있는 칸을 정함.

### EVA 한 번의 흐름

데모가 보여주는 EVA 한 번을 장면 순서로 정리함.

| 장면 | 일어나는 일 | 근거 데이터 | 확인 |
|---|---|---|---|
| 1. 지도 표시 | 기지 5km 안이 3,067칸(칸 약 160m)으로 깔리고 칸마다 생명점수 0~100 이 표시됨. 20점대가 1,924칸으로 가장 많고 델타 전선 핀은 84점 | CRISM 광물맵(S1), USGS 지질맵(S2) | (코드) |
| 2. 목표 선택 | 84점 칸이 과학적으로 1순위. 점수는 가치만 나타내고 도달 가능 여부는 별도 판단 | `grid.js` | (코드) |
| 3. 경로 탐색 | A\* 가 경사와 암석 피복에 비용을 매겨 경로를 고름. 직선 경로 경사 22.7°, 우회 경로 11.2° | CTX DEM 20m, THEMIS 열관성 | 경로 비교는 (기록), 격자 최대 경사 22.7° 와 델타 전선 칸 경사 11.2° 는 (코드) |
| 4. 출발 | 경사 5°, 하중 20kg 에서 심박 143 bpm | Pandolf 대사율, 심박식 | (코드) |
| 5. 급경사 | 12° 에서 179 bpm, 15° 와 25kg 에서 186 bpm(최대심박 상한), %VO₂ 1.15. 산소 소모율 2.87 에서 3.46 L/min 으로 증가 | `data/synthetic_eva.json` | (코드) |
| 6. 복귀선 수축 | 산소가 줄면 왕복 가능 반경이 줄고 반경 밖 목적지는 잠김 | walk-back 모델 | (코드) 데모는 산소 기준만 구현 |
| 7. 교신, 피폭 | 지형에 가린 칸은 `comm=shadow` 로 표시(584칸). 피폭은 기준 0.64 mSv/day 로 누적 | DEM 시선 판정, Curiosity RAD | (코드) |
| 8. 복귀 | 걸은 거리가 복귀 반경에 닿으면 자동 귀환으로 전환. 경사 2°, 하중 15kg 에서 125 bpm | walk-back 모델, 심박식 | (코드) |

## 데이터

### 공개 원본

대용량 원본은 `.gitignore` 로 제외했고 저장소에는 파생물만 들어 있음. 재취득 링크는 [`docs/6_raw_downloads.md`](docs/6_raw_downloads.md) 에 있음.

| 원본 | 내용 | 형식 | 재현 시 경로 | 출처, 라이선스 |
|---|---|---|---|---|
| CRISM 광물맵 | MRO 가시, 근적외 분광계로 Jezero 광물을 분류한 맵 | 래스터 | `zenodo_5575824/jezeroFinal.tif` | Parente, Itoh, Saranathan, Zenodo 5575824, CC-BY-4.0 |
| USGS SIM 3464 지질맵 | Jezero, Nili Planum 지질 유닛 폴리곤 (약 349MB `.gdb`) | 벡터 | `sim3464_extract/sim3464_JezeroNili_FINAL/Geodatabase/Nili.gdb` | Sun & Stack 2020 |
| Jezero CTX DEM 20m | MRO Context Camera 스테레오 고도모델 (약 90MB) | 래스터 | `jezero_dem.tif` | USGS Astrogeology |
| THEMIS 열관성 | Mars Odyssey 열적외 영상 기반 열관성 맵 (약 1.7MB) | 래스터 | `zenodo_4931348/Jezero_Thermal_Inertia_v1.tiff` | Edwards & Buz 2021, Zenodo 4931348, CC-BY-4.0 |
| PhysioNet 트레드밀 최대운동검사 | 심박, VO₂, 속도 동시 기록. 992건, 약 57만 샘플 (기록) | 시계열 CSV | `physionet_data/` | Mongin 외 2021, DOI 10.13026/7ezk-j442, PhysioNet Contributor Review Health Data License 1.5.0 |

### 저장소에 포함된 파생 데이터

| 파일 | 내용 | 확인 |
|---|---|---|
| `grid.geojson` | 최종 격자 GeoJSON. 3,067칸, `cell_m` 160, 기지 좌표 (77.45°E, 18.44°N) | (코드) |
| `grid.js` | 같은 격자의 `window.GRID` 전역판. 내용이 `grid.geojson` 과 동일함 | (코드) |
| `data/s2_jezero.tif` | SIM 3464 를 S2 0~4 로 재코딩한 래스터(약 94KB). 이 파일이 있으면 349MB 원본 없이 격자 재생성 가능 | 파일 존재만 확인 |
| `data/synthetic_eva.json` | 보정 심박식과 Pandolf 로 합성한 EVA 6스텝 | (코드) |
| `data/weights.json` | 지표 순위와 ROC/RS 가중치 | (코드) |
| `data/crew_spec.json`, `consumables.json`, `radiation.json`, `equipment.json` | 모델 상수(문헌값) | 파일 수록 값 |

격자 칸의 속성은 `slope_deg`, `comm`, `S1`~`S5`, `score`, `rock` 임. 필드와 타입은 [`docs/12_api_data_spec.md`](docs/12_api_data_spec.md) 에 정리돼 있음.

### 처리 과정

| 원본 | 정제, 변환 | 산출 | 스크립트 |
|---|---|---|---|
| USGS SIM 3464 | 지질 유닛명을 퇴적, 델타 맥락 기준 S2 0~4 로 재코딩한 뒤 50m 해상도로 래스터화 | `data/s2_jezero.tif` | `scripts/make_s2.py` |
| CRISM 광물맵 | 광물 분류 색을 S1 점수(1, 3, 4)로 변환. 미식별(검정), 배경(흰색)은 null | S1 레이어 | `scripts/build_grid.py` |
| CTX DEM 20m | 경사 `slope_deg` 계산, 안테나 높이 15m 가정의 시선 판정으로 `comm` 산출 | 경사, 교신 레이어 | `scripts/build_grid.py` |
| THEMIS 열관성 | 열관성(TI)을 암석 피복 `rock` 0~1 로 변환. TI 150 이하 0, 350 에서 0.5, 1200 에서 1.0 인 2구간 선형 | 경로 비용 레이어 | `scripts/build_grid.py` |
| PhysioNet 트레드밀 | 검사별 VO₂ 95퍼센타일을 개인 최대로 보고 %VO₂ 로 정규화. 심박 40~220 bpm, VO₂>0 구간만 사용. 유효 샘플 10개 미만 검사 제외. 1차 회귀로 심박식 보정 | `data/synthetic_eva.json` | `scripts/calibrate_hr.py` |
| 지표 순위(문헌) | Barron ROC 공식과 Rank Sum 공식으로 가중치 계산 | `data/weights.json` | `scripts/gen_biosignature.py` |

- 정렬: 해상도와 좌표계가 다른 래스터를 공통 격자(3,067칸, 칸 약 160m, 기지 5km 클립)로 리샘플해 한 칸에 모든 속성이 들어가게 함.
- 결측 처리: 결측 칸을 채우지 않음. 생명점수는 투입된 지표만 가중 재정규화해 계산하고, 커버리지와 점수를 따로 보고함.
- S2 재코딩표, CRISM 색 대 S1 대응, 열관성 구간값은 문헌으로 정한 초기값임.
- 지상 관측 반영: Perseverance 착륙 후 Jezero 바닥이 화성암(Máaz, Séítah)으로 확인돼 `Jezero floor unit` 의 S2 를 2 에서 1 로 낮춤(`scripts/make_s2.py` 의 `NAME2S2`).

데이터셋별 출처와 라이선스 점검은 [`docs/2_sources.md`](docs/2_sources.md), [`COMPLIANCE_CHECK.md`](COMPLIANCE_CHECK.md) 에 있음.

## 방법

### 생명점수

칸마다 과학지표 Sᵢ(0~4)를 가중합해 0~100 으로 환산함.

```
score = Σ(wᵢ·Sᵢ, 투입된 i) / Σ(wᵢ, 투입된 i) / 4 × 100     # 가용 지표만 재정규화
```

가중치 숫자는 직접 고르지 않음. 지표 순위만 문헌(iMOST, Hartz & George 2022)으로 정하고 숫자는 Barron ROC 공식으로 계산함.

| 지표 | 순위 | ROC 가중치 (코드) | RS 가중치 (코드) | 입력 데이터 | 상태 |
|---|---|---|---|---|---|
| S1 함수/점토광물 | 1 | 0.457 | 0.333 | CRISM 광물맵 | 실데이터 투입 |
| S2 퇴적, 델타 맥락 | 2 | 0.257 | 0.267 | USGS SIM 3464 | 실데이터 투입 |
| S4 물 활동 | 3 | 0.157 | 0.200 | CRISM 수화신호, 수로/델타 지형 | 설계 완료, 미적용 |
| S3 보존성 염류 | 4 | 0.090 | 0.133 | THEMIS/CRISM 염류 | 설계 완료, 미적용 |
| S5 로버 현장 근접 | 5 | 0.040 | 0.067 | Perseverance, MSL 확인 노두 | 미투입 |

- 현재 점수의 분모는 S1 과 S2 가중치 합 0.714 임. S1 이 없는 칸은 S2 만으로 계산함.
- S4 를 투입하지 않은 이유: S1(점토)과 S2(델타)가 모두 물로 형성, 퇴적된 지표라 별도로 넣으면 같은 신호를 두 번 셈.
- S3 를 투입하지 않은 이유: Jezero 는 염류가 드물어 변별력이 낮음.
- 번호 규약: 코드 기준 S4 가 물 활동(순위 3), S3 가 염류(순위 4)임.
- 가중치 프리셋 3종(과학권장, 물추적, 검증우선)이 `data/weights.json` 의 `presets_rank` 에 들어 있음.

상세 설계는 [`docs/7_biosignature_design.md`](docs/7_biosignature_design.md) 에 있음.

### 안전 레이어

점수가 100 이어도 복귀선 밖이면 추천하지 않는 구조임.

| 레이어 | 입력 | 쓰는 방식 |
|---|---|---|
| 경사 `slope_deg` | CTX DEM 20m | 25° 초과 칸 통행 차단(초기값). A\* 비용에 대사율 가중으로 반영 |
| 교신 `comm` | 같은 DEM, 안테나 높이 15m 가정(초기값) 시선 판정 | 음영 칸 표시. 데모에서는 음영 칸에 지형 차폐를 적용해 선량을 줄임 |
| 암석 피복 `rock` | THEMIS 열관성 | A\* 간선비용 `×(1+2·rock)`. 하드 차단은 경사가 담당 |
| 복귀선 | 산소 잔량 | 반경 밖 목적지 잠금 |

### 생체 모델 체인

```
경사(DEM) + 하중      →  대사율 M_W (Pandolf)        [NASA JSC EVA traverse 모델]
M_W                   →  산소 소모율 O2_rate         [산소 1L ≈ 20.9 kJ → M_W/348]
O2_rate / VO2abs      →  운동강도 %VO₂               [VO2peak 37.5 ml/kg/min, ISS 승무원]
%VO₂                  →  심박 HR, 체력 stam          [PhysioNet 트레드밀 실측 보정]
산소 잔량             →  왕복 복귀 반경 → 지점 잠금  [walk-back 모델]
```

| 단계 | 공식 | 상수, 출처 | 구현 위치 |
|---|---|---|---|
| 대사율 | `M_W = 1.5·M + 2.0·(M+L)·(L/M)² + η·(M+L)·(1.5·v² + 0.35·v·G·g_mars)` | `M=80`, `η=2.0`(레골리스를 모래로 근사), `g_mars=0.38`. Pandolf 1977, NASA JSC | `calibrate_hr.py`, 데모 |
| 산소 | `O2_rate = M_W / 348` (L/min), 탱크 500 L | 산소 1L ≈ 20.9 kJ | `calibrate_hr.py`, 데모 |
| 운동강도 | `%VO₂ = O2_rate / VO2abs`, `VO2abs = 37.5·80/1000 = 3.0 L/min` | ISS 남성 평균 VO2peak, NTRS 20220014309 | `calibrate_hr.py`, 데모 |
| 심박 | `HR = 70.5 + 113.2·%VO₂`, 상한 `HRmax = 220−34 = 186` | PhysioNet 실측 회귀, R²=0.77 (기록) | `calibrate_hr.py`, 데모 |
| 체력 | `%VO₂ > 0.35` 이면 스텝당 `−14·(%VO₂−0.35)`, 아니면 `+8·(0.35−%VO₂)`, 0~100 범위 | 지속가능 강도 VO2peak 30~40%, W′BAL | 데모 |
| 복귀 반경 | `남은거리 = (o2/TANK)·2000`, `반경 = (남은거리 − 2000·0.15) / 2` | 예비분 15%, 2 로 나누는 것은 왕복. 만충 시 850m | 데모 |
| 피폭 | `dose += (0.64/1440)·shF·Δt`, 음영 칸 `shF = 0.8`, SPE 활성 구간에 `+1.2 mSv·shF` | Curiosity RAD(Hassler 2014), 지형 차폐 최대 약 19%(Guo 2026) | 데모 |

체력 임계 0.35, 예비분 15%, 차폐율 20%, 왕복 한도 2,000m 는 문헌으로 정한 초기값임. 모델 6종의 입출력과 상수는 [`docs/1_model_spec_handoff.md`](docs/1_model_spec_handoff.md) 에 있음.

### 심박식 보정

우주인의 실시간 생체 피드는 공개 데이터가 없음. 그래서 지상 운동생리 실측으로 심박과 운동강도의 관계만 보정하고, 화성 조건(중력, 하중, 경사)은 Pandolf 식으로 계산하도록 역할을 나눔. 심박과 %VO₂ 의 관계가 중력과 무관하다는 가정에 기대는 분리임.

- 사용 데이터: PhysioNet 트레드밀 최대운동검사. Mongin D, García Romero J, Alvero Cruz JR (2021), 말라가대 운동생리학 실험실. DOI [10.13026/7ezk-j442](https://doi.org/10.13026/7ezk-j442).
- 정제: 검사별 VO₂ 95퍼센타일로 %VO₂ 정규화, 심박 40~220 bpm 과 VO₂>0 구간만 사용, 유효 샘플 10개 미만 검사 제외, 회귀는 %VO₂ 0.1 초과 1.2 이하 구간에서 수행 (코드, `scripts/calibrate_hr.py`).
- 보정 결과: `HR = 70.5 + 113.2·%VO₂`, R²=0.77, 검사 992건, 약 57만 샘플 (기록). 원본이 저장소에 없어 회귀를 다시 돌리지 못했음. 계수 자체는 `data/crew_spec.json`, `data/synthetic_eva.json`, 데모의 `HR_A`, `HR_B` 에 들어 있음.
- 보정 전 데모가 쓰던 식은 `70 + 116·%VO₂` 였음 (기록, 스크립트 출력 문구에 남아 있음).

### 다중 소모품 복귀 한계 (설계, 진행 중)

복귀 한계를 산소 하나가 아니라 소모품 4종 중 가장 먼저 바닥나는 것(`min`)으로 정하는 설계임. 용량 데이터는 `data/consumables.json` 에 있고, 지도 데모에는 아직 산소 기준만 구현돼 있음.

| 소모품 | 용량 (아폴로 15~17 PLSS, `data/consumables.json`) | 대사율 비례 | 계수 (기록) |
|---|---|---|---|
| 산소 | 1430 psi | 비례 | 1.0 |
| 냉각수 | 5.2 L (11.5 lb) | 비례 | ×1.05 (열부하) |
| CO₂ 스크러버 (LiOH) | 3.12 lb | 비례 | ×0.95 |
| 배터리 | 390 Wh | 비례 안 함 | 일정 |

- 기준 대사율 `M0 = 273 W`(약 930 BTU/hr)에 대해 `f = M_W / M0` 로 소모율을 스케일함 (기록, `docs/1_model_spec_handoff.md`).
- 지속시간과 작업률 곡선: 930 BTU/hr 에서 8h, 1200 에서 6h, 1600 에서 5h (NTRS 20150009506, `data/consumables.json`).
- 아폴로 12 텔레메트리의 항목별 잔여시간: 산소 2.2h, 냉각수 2.4h, CO₂ 2.1h, 전력 0.72h (NTRS 19720019460, `data/consumables.json`).
- 고강도 짧은 작업은 냉각수와 산소가, 저강도 장시간 작업은 배터리가 먼저 바닥나는 구조임.
- 피폭의 고도 보정 `altF = 1 + 고도/5000` 도 설계 문서에만 있고 데모에는 들어 있지 않음.

## 결과

### 생명점수 격자

`grid.geojson` 을 읽어 다시 집계한 값임. 모두 (코드).

| 항목 | 채워진 칸 | 최소 / 평균 / 최대 | 분포 |
|---|---|---|---|
| S1 | 2,488 / 3,067 (81.1%) | 1 / 2.04 / 4 | 1점 1,396칸, 3점 690칸, 4점 402칸, null 579칸 |
| S2 | 3,067 / 3,067 (100%) | 0.2 / 1.44 / 4.0 | 반올림 기준 0점 9칸, 1점 2,526칸, 2점 74칸, 3점 70칸, 4점 388칸 |
| S3, S4, S5 | 0 | 없음 | 전 칸 null |
| score | 3,067 / 3,067 (100%) | 25 / 42.7 / 100 | 아래 표 |

| score 구간 | 20점대 | 30점대 | 40점대 | 50점대 | 60점대 | 70점대 | 80점대 | 90점대 | 100점 |
|---|---|---|---|---|---|---|---|---|---|
| 칸 수 | 1,924 | 27 | 9 | 341 | 36 | 329 | 279 | 23 | 99 |

- Jezero floor 의 S2 를 2 에서 1 로 낮추기 전 평균은 51.3 이었음 (기록).

### 데모 핀 4개

핀 점수는 그 위치에서 가장 가까운 격자 칸의 score 를 읽은 값임. 반경 800m 안에 점수 칸이 없을 때만 파일의 추정값으로 대체함. 아래는 핀 좌표에 가장 가까운 칸을 직접 조회한 결과임 (코드).

| 핀 | score | S1 | S2 | 경사 | 교신 | rock |
|---|---|---|---|---|---|---|
| 델타 전선 | 84 | 3 | 4.0 | 11.2° | clear | 0.19 |
| Cheyava 방향 | 25 | 1 | 1.0 | 1.3° | clear | 0.07 |
| Hawksbill Gap | 25 | 1 | 1.0 | 1.9° | clear | 0.10 |
| Séítah | 29.5 (표시 30) | 1 | 1.5 | 1.8° | shadow | 0.14 |

### 안전 레이어

| 항목 | 값 | 확인 |
|---|---|---|
| 경사 `slope_deg` | 0.5 / 3.1 / 22.7° (최소 / 평균 / 최대), 25° 초과 칸 0개 | (코드) |
| 교신 `comm` | clear 2,483칸, shadow 584칸 | (코드) |
| 암석 피복 `rock` | 0.00 / 0.14 / 0.32 (최소 / 평균 / 최대), 전 칸 채워짐 | (코드) |
| A\* 경로 | 델타 전선까지 직선 22.7°, 우회 11.2° | (기록) |

### 합성 EVA 시계열

`data/synthetic_eva.json` 의 값이고, 같은 식으로 다시 계산해 일치함을 확인함 (코드). 보행 속도는 1.0 m/s 고정임.

| t (분) | 경사 | 하중 | 대사율 | %VO₂ | 심박 | 산소 소모 | 지속 플래그 | 비고 |
|---|---|---|---|---|---|---|---|---|
| 0 | 5° | 20 kg | 665 W | 0.64 | 143 bpm | 1.91 L/min | 가능 | 완경사 출발 |
| 10 | 12° | 20 kg | 998 W | 0.96 | 179 bpm | 2.87 L/min | 가능 | 오르막 진입, VO2peak 근접 |
| 20 | 15° | 25 kg | 1,204 W | 1.15 | 186 bpm | 3.46 L/min | 불가 | 최대심박 상한, 작업 분할과 휴식 신호 |
| 30 | 5° | 25 kg | 700 W | 0.67 | 146 bpm | 2.01 L/min | 가능 | 경사 완화로 회복 |
| 40 | 8° | 20 kg | 806 W | 0.77 | 158 bpm | 2.32 L/min | 가능 | 복귀 구간 |
| 50 | 2° | 15 kg | 500 W | 0.48 | 125 bpm | 1.44 L/min | 가능 | 기지 접근 |

- 20분 스텝의 강도(3.46 L/min)를 유지하면 500 L 탱크는 약 2.4시간에 소진됨 (코드, 500/3.46/60). 같은 거리라도 급경사 경로에서는 복귀 반경이 더 빨리 줄어듦.

### 대원 제원과 기타 상수

| 항목 | 값 | 출처 (파일) |
|---|---|---|
| 체중 | 80 kg | 대표값 (`data/crew_spec.json`) |
| 나이 | 34 | NASA 후보 평균, NTRS 20240001630 (`data/crew_spec.json`) |
| VO2peak | 37.5 ml/kg/min | ISS 남성 평균, NTRS 20220014309 (`data/crew_spec.json`) |
| 기준 선량 | 0.64 mSv/day | Curiosity RAD, Hassler 2014 (`data/radiation.json`) |
| SPE 스파이크 | 1.2~19.5 mSv | RAD 순항 SPE 관측 (`data/radiation.json`) |
| 지형 차폐 최대 | 20% (실측 최대 19%) | Guo 2026 (`data/radiation.json`) |
| 기본 하중 L | 20 kg | 아폴로 11 지질공구 총질량 22.9 kg 수준 (`data/equipment.json`) |

## 한계

- 실제 환경 시험: 실제 수트 텔레메트리, 실제 대원, 화성 현장 조건에서는 시험하지 못함. 지도 데모는 시나리오 시뮬레이션임.
- 생체 모델: 지상 트레드밀 실측으로 보정한 심박식과 Pandolf 계산의 조합임. 심박과 %VO₂ 관계가 화성 중력과 수트 착용 조건에서도 유지된다는 가정은 검증하지 못함.
- 심박식 재현: PhysioNet 원본이 저장소에 없어 계수 70.5, 113.2 와 R²=0.77, 검사 992건은 (기록) 값임. 원본을 받아 `scripts/calibrate_hr.py` 를 실행하면 다시 확인할 수 있음.
- S5(로버 근접) 미투입: Perseverance 트래버스 레이어를 넣으면 score 가 다시 혼합됨. 진행 중.
- S1 커버리지 81.1%: CRISM 미식별 칸 579개는 보간하지 않고 비워 둠.
- 다중 소모품 복귀 한계와 피폭 고도 보정은 설계 문서와 데이터 파일까지만 있고 데모에는 산소 기준 복귀선만 구현됨. 진행 중.
- 데모의 SPE 처리: 활성 구간 동안 스텝마다 `spike_mSv` 를 더하는 단순화된 방식임. 실제 선량률 곡선이 아님.
- 데모의 산소 소모에는 `O2SCALE=0.80` 스케일이 걸려 있어 `synthetic_eva.json` 의 소모율과 수치가 다름. 복귀선 계산에는 영향이 없음.
- `synthetic_eva.json` 의 `sustainable` 플래그는 %VO₂ 1.0 초과 여부임. 체력 모델의 지속가능 임계 0.35 와 다른 기준이라 구분해서 읽어야 함.
- `data/spots.json` 의 score(92, 85, 78, 54)는 폴백용 추정치임. 실제 표시 점수는 격자에서 읽음. 데모는 `spots.json` 을 불러오지 않고 같은 내용을 인라인으로 가지고 있음.
- 교신 음영은 DEM 시선 근사임. 전파 회절과 중계 위성은 반영하지 않음. DONKI 이벤트 시각은 지구 기준임.
- 경사 차단 25°, 안테나 높이 15m, 예비분 15%, 체력 임계 0.35, S2 재코딩표, 열관성 구간값은 모두 초기값임.
- `data/layers.json` 은 레이어와 게이트의 설계 정의 파일임. 데모와 스크립트는 이 파일을 읽지 않음.
- 데모의 Leaflet 은 CDN 에서 버전 고정 없이 불러옴. 오프라인에서는 지도와 배경 타일이 표시되지 않음.

## 기술 스택

| 구분 | 사용 |
|---|---|
| 전처리 | Python, numpy, pandas, rasterio, pyogrio, shapely |
| 격자 형식 | GeoJSON (`grid.geojson`), JS 전역 (`grid.js`), GeoTIFF (`data/s2_jezero.tif`) |
| 데모 | 단일 HTML, Leaflet, OpenPlanetary 화성 배경 타일 |
| 경로 탐색 | A\* (이진힙, 데모 내 JavaScript 구현) |
| 외부 API 점검 | NASA DONKI, Mars 2020 raw images (`scripts/check_apis.py`, `scripts/fetch_pov.py`) |

## 폴더 구조

```
.
├── README.md
├── LICENSE
├── COMPLIANCE_CHECK.md          규정, 라이선스 점검 기록
├── MARSWALK_전체.md              기능별 데이터 검증 현황 종합 문서
├── marswalk_grid_demo.html      Leaflet 지도 데모
├── grid.js                      최종 격자 (window.GRID)
├── grid.geojson                 같은 격자의 GeoJSON
├── data/
├── scripts/
└── docs/
```

### data/

| 파일 | 내용 |
|---|---|
| `synthetic_eva.json` | 보정 심박식으로 만든 EVA 6스텝(경사, 하중, %VO₂, 심박, 산소 소모) |
| `crew_spec.json` | 대원 제원. 체중 80kg, 나이 34, VO2peak 37.5, 심박식 계수, HRmax 186 |
| `consumables.json` | EVA 소모품 4종의 아폴로 PLSS 용량과 작업률별 지속시간 곡선 |
| `radiation.json` | 피폭 상수. RAD 0.64 mSv/day, 지형 차폐 최대 20%, SPE 스파이크, 고도 효과 |
| `weights.json` | 생명점수 지표, 순위, ROC/RS 가중치, 지표별 선정 근거와 출처 |
| `s2_jezero.tif` | SIM 3464 를 S2 0~4 로 재코딩한 래스터. `build_grid.py --geo` 입력 |
| `layers.json` | 지도 레이어 정의(과학 레이어 5종, 안전 레이어) |
| `spots.json`, `spots.js` | 탐사 지점 4곳(좌표, POV 실사 URL, 메모). `.js` 는 전역판 |
| `pov_candidates.json` | Perseverance raw 이미지 후보 목록(sol, 카메라, 촬영 시각, URL) |
| `equipment.json` | 장비 무게(아폴로 문서값). 하중 L 입력용 |
| `donki_sample.json` | 우주기상 샘플 이벤트(NASA DONKI). SPE 경보 시나리오용 |

### scripts/

| 파일 | 내용 |
|---|---|
| `build_grid.py` | DEM 경사, 교신 + CRISM(S1) + 지질(S2) + THEMIS(rock) 을 격자로 산출 |
| `make_s2.py` | SIM 3464 지질 폴리곤을 유닛별 S2(0~4) 래스터로 변환 |
| `calibrate_hr.py` | PhysioNet 실측으로 심박식 회귀 보정, 합성 EVA 시계열 생성 |
| `gen_biosignature.py` | 지표 순위에서 ROC/RS 가중치 계산 |
| `fetch_pov.py` | Perseverance raw 이미지(델타 POV) 수집 |
| `check_apis.py`, `check_datasets.py` | 외부 NASA API, 데이터셋 접근 점검 |

### docs/

| 파일 | 내용 |
|---|---|
| [`1_model_spec_handoff.md`](docs/1_model_spec_handoff.md) | 모델 6종(대사율, 산소, 복귀선, 체력, 심박, 피폭)의 공식, 입출력, 상수 |
| [`2_sources.md`](docs/2_sources.md) | 상수값 출처 목록과 데이터셋 라이선스 |
| [`3_data_reference.md`](docs/3_data_reference.md) | 외부 NASA 데이터 6계열과 저장 패턴 |
| [`4_decision_log.md`](docs/4_decision_log.md) | 설계 결정 로그 |
| [`5_page_verification.md`](docs/5_page_verification.md) | 페이지별 요소, 데이터, 파일, 근거, 상태 목록 |
| [`6_raw_downloads.md`](docs/6_raw_downloads.md) | 원본 데이터 다운로드 링크 |
| [`7_biosignature_design.md`](docs/7_biosignature_design.md) | 생명점수 상세 설계 |
| [`8_grid_guide.md`](docs/8_grid_guide.md) | `build_grid.py` 격자 전처리 가이드 |
| [`9_verification_status.md`](docs/9_verification_status.md) | 생명점수 격자 검증 현황 |
| [`10_todo.md`](docs/10_todo.md) | 남은 작업 목록 |
| [`11_hud_spec.md`](docs/11_hud_spec.md) | HUD 데이터 매핑 명세 |
| [`12_api_data_spec.md`](docs/12_api_data_spec.md) | 데이터, API 계약서. React + Leaflet 프론트 이식용 |

## 실행 방법

### 데모만 보기

원본 데이터가 필요 없음. `grid.js` 가 최종 산출물임.

```bash
python -m http.server 8000
# 브라우저에서 http://localhost:8000/marswalk_grid_demo.html
```

`marswalk_grid_demo.html` 을 파일로 직접 열어도 지도는 동작하고, 이 경우 `data/donki_sample.json` 대신 인라인 기본값을 씀. Leaflet 과 배경 타일을 받기 위해 네트워크 연결이 필요함.

### 격자 다시 만들기

의존성 설치 후 저장소 루트에서 실행함. 원본은 위 데이터 절의 경로에 둠.

```bash
pip install rasterio numpy pyogrio shapely pandas

# 1) 지질맵 → S2 래스터 (SIM 3464 원본 필요. data/s2_jezero.tif 가 이미 있으면 생략 가능)
python scripts/make_s2.py             # → data/s2_jezero.tif

# 2) 생명점수 격자 (S1 CRISM + S2 지질 + DEM 경사/교신 + rock 열관성)
python scripts/build_grid.py --dem jezero_dem.tif \
  --crism zenodo_5575824/jezeroFinal.tif \
  --geo data/s2_jezero.tif --geo-scored \
  --rock zenodo_4931348/Jezero_Thermal_Inertia_v1.tiff \
  --out grid.js --clip-km 5 --cell-px 8 --antenna-h 15

# 3) 심박식 보정 + 합성 EVA 시계열 (PhysioNet 원본을 ./physionet_data/ 에 받은 뒤)
python scripts/calibrate_hr.py        # → data/synthetic_eva.json, 계수와 R² 는 콘솔 출력

# 4) 생명점수 가중치 (어디서 실행해도 저장소의 data/weights.json 에 씀)
python scripts/gen_biosignature.py    # → data/weights.json
```

출력 `grid.js` 를 `marswalk_grid_demo.html` 옆에 두면 데모가 자동으로 읽음. 이번 정리에서는 원본 데이터가 없어 1~3 단계를 다시 실행하지 못했고, 저장소에 있는 산출물만 대조함. 4 단계는 다시 실행해 기존 `data/weights.json` 과 같은 결과가 나옴을 확인함.

## 출처

지도, 과학

- S1 CRISM 광물맵: Parente, Itoh, Saranathan, Zenodo 5575824, https://doi.org/10.5281/zenodo.5575824 (CC-BY-4.0)
- S2 지질맵: Sun, V. Z. & Stack, K. M. (2020) USGS SIM 3464, https://doi.org/10.3133/sim3464
- 암석 피복: Edwards & Buz (2021) THEMIS Jezero TI, https://doi.org/10.5281/zenodo.4931348 (CC-BY-4.0)
- 보존 근거: Broz (2020) *Life* 10.3390/life10070113, iMOST (Des Marais 2018, NTRS 20180003291), Hickman-Lewis 2025 (Nat. Commun. 10.1038/s41467-025-57727-4)
- 가중치 공식: Barron & Barrett (1996) *Management Science* 42(11):1515-1523, Barron (1992) ROC, Stillwell (1981) RS

생체, 사람

- 심박 실측: Mongin D, García Romero J, Alvero Cruz JR (2021) "Treadmill maximal exercise tests from the Exercise Physiology and Human Performance Lab of the University of Malaga" (v1.0.1), PhysioNet, https://doi.org/10.13026/7ezk-j442, PhysioNet Contributor Review Health Data License 1.5.0. 플랫폼 인용 Pollard TJ, et al. (2026) *Nature Health*
- 대사율: Pandolf (1977), NASA JSC EVA traverse 모델
- VO2peak, 지속가능 강도: NTRS 20220014309 (ISS 승무원), Coats 2003, W′BAL
- 소모품: 아폴로 15~17 PLSS, EMU 지속시간과 작업률 NTRS 20150009506, 아폴로 12 텔레메트리 NTRS 19720019460
- 피폭: Hassler (2014) *Science* 10.1126/science.1244797 (Curiosity RAD), Guo (2026) *JGR Planets* 10.1029/2026JE009704 (지형 차폐)

## 라이선스

[MIT](LICENSE). 코드와 문서에 적용되며 외부 데이터셋은 각 원본 라이선스를 따름.
