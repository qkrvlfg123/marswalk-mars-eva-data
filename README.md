# MARSWALK — 화성 Jezero EVA 데이터

화성 기지 대원의 **선외활동(EVA, Extra-Vehicular Activity)** 의사결정 보조 데모 중 **데이터 파트**임.
한 번의 도보 EVA에서 동시에 답해야 하는 두 가지, **"어디로 갈까"(생명점수)** 와 **"안전하게 다녀올 수 있나"(복귀선·경사·교신·피폭·생체 신호)** 를 각각 공개 데이터로 채움.
앱은 추천·경고만 하고 최종 go/no-go는 우주인이 판단함(안전 최우선).

> 팀 **team-navis**의 NASA Space Apps Challenge 2026 (Seoul) 제출작 중 데이터 파트임.
> 이 저장소의 데이터 수집·정제·격자 산출을 박혜윤([@qkrvlfg123](https://github.com/qkrvlfg123))이 담당했고, 그 작업을 공개 데이터 기반으로 재현 가능하게 정리함. 메인 3D 데모는 팀 저장소에 있음.
>
> 최신 갱신: **2026-11-15** — 생명점수가 S1·S2 실데이터로 채워져 전 칸 100% 커버리지.

---

## 1. 이야기 — 어느 EVA 한 번

Jezero 크레이터. 기지에서 걸어 나갈 수 있는 거리는 **왕복 2km**가 전부고, 등에 멘 산소는 **500 L(약 8시간)** 임. 대원은 아침에 지도를 열고 "오늘 어디를 볼지"를 고름. 이 데모가 보여주는 한 번의 EVA는 아래 순서로 흘러감.

| 장면 | 일어나는 일 | 이 장면을 만든 데이터 |
|---|---|---|
| **① 지도를 켬** | 기지 5km 안이 3,067칸(칸≈160m)으로 깔리고 칸마다 생명점수 0~100이 찍힘. 대부분 20점대인데 **델타 전선 한 곳만 84점** | CRISM 광물맵(S1) + USGS 지질맵(S2) |
| **② 목표를 고름** | 84점 칸이 과학적으로 1순위. 다만 점수는 "가치"일 뿐이고 갈 수 있는지는 아직 모름 | 생명점수 격자 `grid.js` |
| **③ 길을 찾음** | 직선으로 가면 **경사 22.7°**. A\*가 경사·암석 비용을 물려 **11.2°** 우회로를 뽑고 모래밭 대신 단단한 쪽으로 돌림 | CTX DEM 20m(경사) + THEMIS 열관성(`rock`) |
| **④ 걸음을 시작함** | 오르막 5°·하중 20kg에서 **심박 143 bpm**. 아직 여유 | Pandolf 대사율 + PhysioNet 보정 심박식 |
| **⑤ 급경사 구간** | 12° 구간에서 **179 bpm**, 15°·25kg에서 **186 bpm(최대심박 상한)** · %VO₂ 1.15로 지속 불가. 산소 소모율이 2.87→3.46 L/min으로 뛰고 체력이 깎임 | `data/synthetic_eva.json`(실측 보정 시계열) |
| **⑥ 복귀선이 조여옴** | 산소가 줄면 왕복 가능 반경이 수축함. 멀리 있는 고득점 칸이 **자동으로 잠김** — 산소 90%라도 멀면 잠기고, 20%라도 가까우면 통과 | walk-back 모델 + 아폴로 PLSS 소모품 실측 |
| **⑦ 교신·피폭 확인** | 지형에 가려 교신 음영(`comm=shadow`)인 칸은 회피 큐로 뜨고, 피폭은 분당 누적됨(기준 0.64 mSv/day) | DEM 시선 판정 + Curiosity RAD |
| **⑧ 복귀** | 기지 거리 = 복귀 반경이 되는 순간이 **복귀 불능점**. 넘기면 자동 귀환 트리거. 내려오는 길은 2°·15kg로 **125 bpm**까지 떨어짐 | walk-back 모델 + 심박·체력 모델 |

이 흐름에서 **지도(땅)와 생체 신호(사람)는 한 체인으로 묶여 있음.** 경사가 바뀌면 심박과 산소 소모율이 바뀌고, 그게 복귀 반경을 바꾸고, 복귀 반경이 갈 수 있는 칸을 바꿈. 아래 2·3절이 각각 사람 쪽 데이터와 땅 쪽 데이터임.

---

## 2. 생체 신호 — 사람 쪽 데이터

### 2.1 체인

경사·하중이 심박으로, 심박이 "오늘 어디까지 갈 수 있나"로 번역되는 경로임. 추정으로 메운 칸이 없도록 각 단계를 실측·논문값으로 받침.

```
경사(DEM) + 하중      →  대사율 M_W (Pandolf)        [NASA JSC EVA traverse 모델]
M_W                   →  산소 소모율 O2_rate         [산소 1L ≈ 20.9 kJ → M_W/348]
O2_rate / VO2abs      →  운동강도 %VO₂               [VO2peak 37.5 ml/kg/min, ISS 승무원]
%VO₂                  →  심박 HR · 체력 stam         [PhysioNet 992건 실측 보정]
산소 잔량             →  왕복 복귀 반경 → 지점 잠금  [아폴로 15-17 PLSS 실측 용량]
```

| 단계 | 공식 | 상수·출처 |
|---|---|---|
| 대사율 | `M_W = 1.5·M + 2.0·(M+L)·(L/M)² + η·(M+L)·(1.5·v² + 0.35·v·G·g_mars)` | `η=2.0`(레골리스≈모래), `g_mars=0.38` · Pandolf 1977 / NASA JSC |
| 산소 | `O2_rate = M_W / 348` (L/min), 탱크 500 L ≈ 8h | 산소 1L ≈ 20.9 kJ |
| 운동강도 | `%VO₂ = O2_rate / VO2abs`, `VO2abs = 37.5·80/1000 = 3.0 L/min` | ISS 남성 평균 VO2peak · NTRS 20220014309 |
| **심박** | **`HR = 70.5 + 113.2·%VO₂`** (R²=0.77), 상한 `HRmax = 220−34 = 186` | **PhysioNet 트레드밀 992건 실측 보정** |
| 체력 | `%VO₂ > 0.35` → 분당 `−14·(%VO₂−0.35)`, 아래면 `+8·(0.35−%VO₂)` (0~100 범위) | 지속가능 강도 VO2peak 30~40% · W′BAL(critical power) |
| 복귀 반경 | `남은거리 = (o2/TANK)·2000`, `반경 = (남은거리 − 2000·0.15) / 2` | 예비분 15%, **÷2 = 왕복**(편도로 쓰면 고립) |

### 2.2 심박식을 실측으로 보정한 과정

우주인의 실시간 생체 피드는 공개 데이터가 없음. 그래서 **지상 운동생리 실측으로 심박↔운동강도 곡선만 보정하고, 화성 조건(중력·하중·경사)은 Pandolf로 계산**하는 식으로 역할을 나눔. 심박-%VO₂ 관계는 중력에 의존하지 않는 보편 생리라 이 분리가 성립함.

- **쓴 데이터:** PhysioNet 트레드밀 최대운동검사 — **992건 검사, 약 57만 샘플**(심박·VO₂·속도 동시 기록). Mongin D, García Romero J, Alvero Cruz JR (2021), 말라가대 운동생리학 실험실.
  DOI [10.13026/7ezk-j442](https://doi.org/10.13026/7ezk-j442) · 라이선스 PhysioNet Contributor Review Health Data License 1.5.0
- **정제:** 검사별로 VO₂ 95퍼센타일을 개인 최대로 잡아 `%VO₂`로 정규화 → 심박 40~220 bpm·VO₂>0 구간만 남김 → 유효 샘플 10개 미만 검사는 제외.
- **보정 결과:** 전 샘플 1차 회귀로 **`HR = 70.5 + 113.2·%VO₂` (R²=0.77)**. 데모가 쓰던 눈대중 값(`70 + 116·%VO₂`)과 거의 같은 값이 실측에서 나와 모델을 실측 기반으로 교체할 근거가 됨. `marswalk_grid_demo.html`도 이 보정값(`HR_A=70.5`, `HR_B=113.2`, HRmax 186 캡)으로 돌아감.
- **산출:** 보정 곡선 + Pandolf(화성 중력 반영)로 EVA 시나리오 6스텝을 합성 → `data/synthetic_eva.json`.
- **스크립트:** [`scripts/calibrate_hr.py`](scripts/calibrate_hr.py)

### 2.3 합성 EVA 시계열 (`data/synthetic_eva.json`)

위 보정 곡선으로 만든, 1절 이야기의 수치 원본임. 경사·하중만 바꿔 넣으면 심박·산소가 따라 나옴.

| t (분) | 경사 | 하중 | %VO₂ | 심박 | 산소 소모 | 지속 플래그 | 읽는 법 |
|---|---|---|---|---|---|---|---|
| 0 | 5° | 20 kg | 0.64 | 143 bpm | 1.91 L/min | 가능 | 완경사 출발 |
| 10 | 12° | 20 kg | 0.96 | 179 bpm | 2.87 L/min | 가능 | 오르막 진입, VO2peak 근접 |
| 20 | 15° | 25 kg | 1.15 | **186 bpm** | 3.46 L/min | **불가** | 최대심박 상한 · 작업 분할·휴식 신호 |
| 30 | 5° | 25 kg | 0.67 | 146 bpm | 2.01 L/min | 가능 | 경사 완화로 회복 |
| 40 | 8° | 20 kg | 0.77 | 158 bpm | 2.32 L/min | 가능 | 복귀 구간 |
| 50 | 2° | 15 kg | 0.48 | 125 bpm | 1.44 L/min | 가능 | 기지 접근 |

20분 스텝 하나가 산소를 분당 3.46 L씩 먹음 — 500 L 탱크에서 **그 강도만 유지하면 2.4시간**밖에 못 버팀. 같은 거리라도 급경사로 가면 복귀 반경이 훨씬 빨리 줄어든다는 게 이 표의 요점임.

### 2.4 생체 신호가 복귀 한계를 정하는 부분

복귀 한계는 산소 하나가 아니라 **소모품 4종 중 제일 먼저 바닥나는 것**이 정함(`min`). 대사율에 비례하는 항목(산소·냉각수·CO₂)은 생체 신호를 그대로 따라가고, 배터리는 일정하게 빠짐.

| 소모품 | 용량(아폴로 15-17 PLSS 실측) | 대사율 비례 |
|---|---|---|
| 산소 | 1430 psi | 비례 |
| 냉각수 | 5.2 L (11.5 lb) | 비례 (×1.05, 열부하) |
| CO₂ 스크러버 (LiOH) | 3.12 lb | 비례 (×0.95) |
| 배터리 | 390 Wh | 비례 안 함 |

기준 대사율 `M0 = 273 W`(≈930 BTU/hr)에 대해 `f = M_W / M0`로 소모율을 스케일함. 지속시간-작업률 곡선은 930 BTU/hr → 8h, 1200 → 6h, 1600 → 5h (NTRS 20150009506). 아폴로 12 텔레메트리에서도 잔여시간이 항목별로 갈림(산소 2.2h·냉각수 2.4h·CO₂ 2.1h·전력 0.72h, NTRS 19720019460) — 그래서 단일 소모품이 아니라 `min`으로 봄.

- **고강도 짧은 작업** → 냉각수·산소가 먼저 바닥남
- **저강도 장시간** → 배터리가 먼저 바닥남

피폭도 체류 시간에 묶임: `dose += (0.64/1440)·altF·shF·Δt`, `altF = 1 + 고도/5000`, `shF = 1 − 0.2·차폐율`(지형 차폐 최대 ~19% 실측, Guo 2026), 태양입자이벤트(SPE) 시 `+1.2 mSv`. 기준선량은 Curiosity RAD 직접측정(Hassler 2014).

---

## 3. 지도 쪽 데이터 — 생명점수 (Biosignature Score)

칸(cell)마다 과학지표 Sᵢ(0~4) 5개를 ROC 가중치로 가중합해 0~100으로 환산함.

```
score = Σ(wᵢ·Sᵢ, 투입된 i) / Σ(wᵢ, 투입된 i) / 4 × 100     # 가용 지표만 재정규화, 가짜값 안 채움
```

가중치는 손으로 고르지 않음. 지표 **순위**만 과학 문헌(iMOST, Hartz & George 2022)으로 정하고, 숫자는 **Barron ROC 공식**이 계산함 — 0.457 / 0.257 / 0.157 / 0.090 / 0.040.

| 지표 | 쓴 데이터 (이게 무슨 데이터인지) | 상태 | 커버리지 |
|---|---|---|---|
| **S1** 함수/점토광물 | **CRISM 광물맵** — MRO 탑재 가시·근적외 분광계로 Jezero 광물을 분류한 맵(Zenodo 5575824, Parente·Itoh·Saranathan). 점토·탄산염 세기를 0~4로 정규화 | 실데이터 | 2,488/3,067 (81.1%) |
| **S2** 퇴적·델타 맥락 | **USGS 지질맵 SIM 3464** — Jezero·Nili Planum 지질 유닛 폴리곤 지도(Sun & Stack 2020). 유닛별로 퇴적·델타 맥락을 0~4로 재코딩 | 실데이터 | 3,067/3,067 (100%) |
| **S4** 물 활동 · **S3** 염류 | S1·S2에 내재 / Jezero 염류 희박 | 설계완료·비적용 | — |
| **S5** 로버 근접 | Perseverance·MSL 현장 확인 노두 | 미투입(유일) | — |

- **S4·S3를 설계완료·비적용으로 둔 근거:** **S4 물 활동**은 S1(점토)과 S2(델타)가 *둘 다 물로 형성·퇴적된 지표*라 이미 반영됨 — 별도 투입하면 같은 물 신호를 이중계산함. **S3 염류**는 Jezero가 염류 희박(주 신호가 점토·탄산염·델타)이라 변별력이 낮음. 둘 다 루브릭·가중치(ROC)는 설계로 유지하되 Jezero엔 투입하지 않음. 실제 미투입은 **S5 하나**임. (번호 규약: 코드 기준 S4=물활동 순위3·ROC .157, S3=염류 순위4·ROC .09)
- **결과 분포:** score 커버리지 100%(3,067칸), min/평균/max = **25 / 42.7 / 100**.
- **Jezero floor = S2 1:** 지질맵 작성 당시 바닥은 퇴적·화성암 혼재로 해석돼 S2=2였음. Perseverance 착륙 후 바닥이 화성암(Máaz 분출암 / Séítah 올리빈-휘석 화성암질)으로 확인돼 **S2 2→1로 하향**. 평균이 51.3→42.7로 내려갔고 델타 팬(S2=4)은 그대로라 "평범한 화성암 바닥 vs 희귀한 델타 퇴적지" 대비가 선명해짐.
- **데모 핀은 하드코딩이 아님:** 그 위치의 격자 score(실데이터)를 반경 800m 안에서 읽음 — 델타 전선 **84**, Cheyava 25, Hawksbill 25, Séítah ~30. 델타 전선만 홀로 높아 1순위가 뚜렷함.

### 안전 레이어 (점수에 더하지 않고 게이트·경로비용으로만 씀)

과학 점수와 안전은 섞지 않음. 점수가 100이어도 복귀선 밖이면 추천하지 않고 사유와 함께 회색 처리함.

| 레이어 | 쓴 데이터 (이게 무슨 데이터인지) | 쓰는 방식 |
|---|---|---|
| 경사 `slope_deg` | **Jezero CTX DEM 20m** — MRO Context Camera 스테레오로 만든 20m 해상도 고도모델(USGS) | 급경사 차단 게이트 · A\* 비용 |
| 교신 `comm` | 같은 DEM으로 안테나 높이 15m 가정 **시선(LOS) 판정** | 음영 칸 회피 큐 |
| 암석 피복 `rock` | **THEMIS 열관성** — Mars Odyssey 열적외 영상 기반 열관성 맵(Zenodo 4931348, Edwards & Buz 2021). 낮은 TI=모래, 높은 TI=바위 → `rock` 0~1로 변환 | A\* 간선비용 `×(1+2·rock)` → 바위밭 우회 |

A\* 경로탐색 검증: 델타 전선까지 직선 **22.7° → 우회 11.2°**. 바닥 `rock`은 0~0.32 범위.

---

## 4. 데이터 처리 과정 (원본 → 정제 → 격자)

여러 기관의 공개 원본을 모아 **같은 좌표계·같은 격자**로 정렬하고, 결측을 메우지 않는 원칙으로 생명점수·안전 레이어·생체 모델을 만듦. 원본 형식이 제각각(폴리곤·래스터·시계열·표)이라 정제 방식도 달랐음.

| 원본 (공개 데이터) | 형식 | 정제·변환 | 산출 | 스크립트 |
|---|---|---|---|---|
| USGS SIM3464 Jezero 지질맵 (~349MB `.gdb`) | 벡터 폴리곤 | 지질 유닛을 퇴적·델타 맥락 기준 **S2 0~4로 재코딩** 후 격자 해상도로 래스터화 | `data/s2_jezero.tif` | `make_s2.py` |
| CRISM 광물맵 (Zenodo 5575824) | 래스터 | 함수/점토광물 세기를 **S1 0~4로 정규화**, 결측 칸은 가짜값 없이 커버리지(81%)로 표기 | S1 레이어 | `build_grid.py` |
| Jezero CTX DEM 20m (USGS) | 래스터(고도) | 경사(`slope_deg`) 계산 + 안테나 높이 15m 가정 **시선 교신(`comm`)** 판정 | 경사·교신 레이어 | `build_grid.py` |
| THEMIS 열관성 (Zenodo 4931348) | 래스터 | 열관성 → **암석 피복 `rock` 0~1**로 변환(낮은 TI=모래, 높은 TI=바위) | 경로비용 레이어 | `build_grid.py` |
| PhysioNet 트레드밀 (992건, 57만 샘플) | 생체 시계열 | %VO₂ 정규화·이상치 제거 후 회귀로 **심박식 보정**(HR=70.5+113.2·%VO₂, R²=0.77) → 합성 EVA 시계열 생성 | `data/synthetic_eva.json` | `calibrate_hr.py` |
| 지표 순위 (문헌 ROC) | 표 | Barron 공식으로 **ROC/RS 가중치 산출** | `data/weights.json` | `gen_biosignature.py` |

- **정렬:** 해상도·좌표계가 제각각인 래스터들을 **공통 격자(3,067칸, 칸≈160m, 기지 5km 클립)** 로 리샘플해 한 칸에 모든 지표가 같이 들어오게 맞춤.
- **결측을 메우지 않음:** 생명점수는 **투입된 지표만 가중 재정규화**해 산출함(가짜값 미충전). 그래서 커버리지와 점수를 분리해 보고함.
- **대용량 원본은 미포함:** `.gitignore`로 원본(합계 수백 MB)을 빼고 **파생물(`grid.*`, `s2_jezero.tif`)만** 담음. 원본 재취득 링크는 [`docs/6_raw_downloads.md`](docs/6_raw_downloads.md). S2는 `s2_jezero.tif`만 있으면 349MB 원본 없이 격자 재생성이 됨.
- **지상 검증 반영:** Perseverance 착륙 후 Jezero 바닥이 화성암으로 확인돼 S2 기본값을 '퇴적'에서 하향하는 등, 새 사실에 맞춰 코딩을 갱신함.

데이터셋별 라이선스·출처 점검은 [`docs/2_sources.md`](docs/2_sources.md)와 [`COMPLIANCE_CHECK.md`](COMPLIANCE_CHECK.md)에 정리돼 있음.

---

## 5. 재현 (파이프라인)

```bash
# 1) 지질맵 → S2 래스터 (SIM3464 GeoUnits_v1 폴리곤 → 유닛별 S2 0~4)
python scripts/make_s2.py             # → data/s2_jezero.tif

# 2) 생명점수 격자 (S1 CRISM + S2 지질 + DEM 경사/교신 + rock 열관성)
python scripts/build_grid.py --dem jezero_dem.tif \
  --crism zenodo_5575824/jezeroFinal.tif \
  --geo data/s2_jezero.tif --geo-scored \
  --rock zenodo_4931348/Jezero_Thermal_Inertia_v1.tiff \
  --out grid.js --clip-km 5 --cell-px 8 --antenna-h 15

# 3) 생체 신호 — 심박식 실측 보정 + 합성 EVA 시계열
#    PhysioNet 원본을 ./physionet_data/ 에 받은 뒤 실행 (보정계수·R²는 콘솔 출력)
python scripts/calibrate_hr.py        # → data/synthetic_eva.json

# 4) 생명점수 가중치 (지표 순위 → ROC/RS 숫자)
python scripts/gen_biosignature.py    # → data/weights.json
```

의존성: `pip install rasterio numpy pyogrio shapely pandas`. 출력 `grid.js`(`window.GRID`)를 `marswalk_grid_demo.html` 옆에 두면 지도 데모가 자동 로드함.

---

## 6. repo 구조 — 파일별 설명

> 정본 단일 구조: `/README.md` · `/marswalk_grid_demo.html` · `/grid.geojson` · `/grid.js` · `/data` · `/scripts` · `/docs`(1~12). **대용량 원본(DEM·CRISM·THEMIS·SIM3464·PhysioNet)은 미포함(.gitignore)** — 재현 시 `docs/6_raw_downloads.md` 링크로 받으면 됨. 배포 zip은 GitHub Releases로.

**루트**

| 파일 | 이게 뭐다 |
|---|---|
| `README.md` | 이 문서 — 프로젝트 개요·생체 신호·생명점수·재현법·전체 파일 설명 |
| `marswalk_grid_demo.html` | Leaflet 지도 데모 — 경사 히트맵 + 생명점수 핀 + EVA 소모품·복귀선·심박 시뮬. 옆의 `grid.js` 자동 로드 |
| `grid.js` | **최종 격자**(3,067칸, 칸≈160m, 기지 5km 클립) — `window.GRID` 전역. 데모가 직접 읽음 |
| `grid.geojson` | 동일 격자의 **순수 GeoJSON** — React/Leaflet 프론트에서 `fetch()`용 |

**docs/ — 설계·검증 문서(md)**

| 파일 | 이게 뭐다 |
|---|---|
| `1_model_spec_handoff.md` | 모델 6종(대사율·산소·복귀선·체력·심박·피폭) 공식·입출력·상수 — 개발 이식용 |
| `2_sources.md` | 모든 상수값의 출처 목록(논문·실측)과 데이터셋 라이선스 |
| `3_data_reference.md` | 외부 NASA 데이터 6계열·저장 패턴(스트리밍/격자/캐시/상수) |
| `4_decision_log.md` | 설계 결정 로그(정체성·양면 UI·동적 복귀선) |
| `5_page_verification.md` | 패드 페이지별 요소→데이터→파일→근거→상태 매니페스트 |
| `6_raw_downloads.md` | **실측·원본 데이터 RAW 다운로드 링크** — 제외된 대용량 원본 취득처 |
| `7_biosignature_design.md` | 생명점수 상세 설계 — 지표 순위·ROC 가중치·S1/S2 루브릭·구현 현황 |
| `8_grid_guide.md` | `build_grid.py` 격자 전처리 가이드(속성·실행·앱 연동) |
| `9_verification_status.md` | 생명점수 격자 검증 현황 — 커버리지·score 분포·핀 4개 |
| `10_todo.md` | 추후 할 일(TODO) — 개발 전환·데이터 조이기 |
| `11_hud_spec.md` | HUD 데이터 매핑 명세 — 현장(HUD) 요소가 PAD의 어느 데이터·모델을 읽나 |
| `12_api_data_spec.md` | **데이터·API 계약서** — grid.geojson/data json 실제 필드·타입, 모델 함수 시그니처·상수, 런타임 흐름. React+Leaflet+Recharts+Zustand 이식용 |

**data/ — 앱 입력 데이터**

| 파일 | 이게 뭐다 |
|---|---|
| `synthetic_eva.json` | **생체 시계열** — PhysioNet 992건 실측 보정식으로 만든 EVA 6스텝(경사·하중·%VO₂·심박·산소 소모) |
| `crew_spec.json` | **대원 제원** — 체중 80kg·나이 34(NASA 후보 평균)·VO2peak 37.5(ISS 남성 평균)·심박식 계수·HRmax 186 |
| `consumables.json` | **EVA 소모품 4종**(산소·냉각수·CO₂·배터리) 아폴로 PLSS 실측 용량 + 작업률별 지속시간 곡선 |
| `radiation.json` | 피폭 상수 — RAD 0.64 mSv/day·지형차폐 최대 20%·SPE 스파이크·고도 효과 |
| `weights.json` | 생명점수 지표·순위·ROC/RS 가중치(숫자는 Barron 공식 계산) + 지표별 선정 근거·출처 |
| `s2_jezero.tif` | **SIM3464→S2 래스터**(0~4, ~94KB). `build_grid.py --geo` 입력. 이것만 있으면 349MB 원본 없이 grid 재생성 가능 |
| `layers.json` | 지도 레이어 5종 정의(경사·지질·방사선·열·광학). 안전레이어에 `rock`(THEMIS 열관성) 포함 |
| `spots.json` / `spots.js` | 탐사 지점(좌표·POV 실사 URL·메모). `.js`는 `window` 전역판 |
| `equipment.json` | 장비 무게(대표값) — 하중 L 입력용 |
| `donki_sample.json` | 우주기상 샘플 이벤트(NASA DONKI) — SPE 경보 시나리오용 |

**scripts/ — 전처리·취득 스크립트(py)**

| 파일 | 이게 뭐다 |
|---|---|
| `build_grid.py` | 최신 본체. DEM 경사·교신 + CRISM(S1) + 지질(S2) + THEMIS(rock) → `grid.js`/`grid.geojson` |
| `make_s2.py` | USGS SIM3464 지질 폴리곤 → 유닛별 S2(0~4) 래스터 `data/s2_jezero.tif` |
| `calibrate_hr.py` | **생체 신호 처리** — PhysioNet 실측으로 심박식 회귀 보정 + 합성 EVA 시계열 생성 |
| `gen_biosignature.py` | 생명점수 가중치 생성기(지표 순위→ROC/RS 숫자) → `weights.json` |
| `fetch_pov.py` | Perseverance raw 이미지(델타 POV) 수집 |
| `check_apis.py` / `check_datasets.py` | 외부 NASA API·데이터셋 접근 가능 점검 |

### 재현에 필요한 대용량 원본 (레포 미포함) — `docs/6_raw_downloads.md`

| 원본 | 놓을 경로(재현 시) | 출처 |
|---|---|---|
| Jezero CTX DEM 20m (~90MB) | `jezero_dem.tif` | USGS Astrogeology / Mars Trek |
| CRISM 광물맵 | `zenodo_5575824/jezeroFinal.tif` | Zenodo 5575824 |
| THEMIS 열관성 (~1.7MB) | `zenodo_4931348/Jezero_Thermal_Inertia_v1.tiff` | Zenodo 4931348 (Edwards & Buz 2021) |
| USGS SIM3464 지질맵 (~349MB) | `sim3464_extract/…/Nili.gdb` | USGS SIM 3464 |
| PhysioNet 트레드밀 (심박 원본) | `physionet_data/` | PhysioNet DOI 10.13026/7ezk-j442 |

> 프론트엔드만 돌릴 거면 원본이 필요 없음 — `grid.js`/`grid.geojson`가 이미 최종 산출물임. 원본은 격자를 **다시 만들 때**만 필요함(S2는 `data/s2_jezero.tif`가 들어 있어 SIM3464 원본 없이도 재생성됨).

---

## 7. 한계와 알려진 차이

실데이터로 못 채운 부분과 문서·구현 사이의 차이를 숨기지 않고 적음.

- **S5(로버 근접) 미투입** — Perseverance 트래버스 레이어를 넣으면 score가 자동 재혼합됨. 남은 과학지표 중 유일한 공백.
- **S1 커버리지 81.1%** — CRISM 미식별(검정) 칸은 보간하지 않고 비워 둠. 점수는 가용 지표만 재정규화해 산출.
- **생체 신호는 지상 실측 보정 + 화성 조건 계산의 조합** — 우주인 실시간 생체 피드는 공개 데이터가 없음. 심박↔%VO₂ 곡선만 PhysioNet 실측으로 받치고, 화성 중력·하중·경사는 Pandolf로 계산함. 실제 수트 텔레메트리로 교체 가능한 구조.
- **`synthetic_eva.json`의 `sustainable` 플래그 기준** — %VO₂ 1.0(VO2peak 도달) 초과 여부임. 체력(W′) 모델의 지속가능 임계 **0.35**와는 다른 기준이라 둘을 구분해 읽어야 함. 파일의 `_sustainable_def` 키와 `calibrate_hr.py`의 `AEROBIC_CAP` 상수에 이 정의를 박아 둠.
- **`spots.json`의 score 값은 폴백용 추정치** — 실제 표시 점수는 격자(`grid.js`)에서 읽음. 핀 반경 800m 안에 점수 칸이 없을 때만 파일값으로 떨어짐.
- **교신 음영은 DEM 시선 근사** — 실제 전파 회절·중계는 반영하지 않음. DONKI 이벤트 시각은 지구 기준.

---

## 8. 출처

**지도·과학**
- **S1** CRISM 광물맵 — Parente, Itoh, Saranathan, Zenodo 5575824 — https://doi.org/10.5281/zenodo.5575824 (CC-BY-4.0)
- **S2** 지질맵 — Sun, V. Z. & Stack, K. M. (2020) USGS SIM 3464 — https://doi.org/10.3133/sim3464
- **암석 피복(rock)** 열관성 — Edwards & Buz (2021) THEMIS Jezero TI — https://doi.org/10.5281/zenodo.4931348 (CC-BY-4.0)
- **보존 근거** — Broz (2020) *Life* 10.3390/life10070113 · iMOST (Des Marais 2018, NTRS 20180003291) · Hickman-Lewis 2025 (Nat. Commun. 10.1038/s41467-025-57727-4)
- **가중치 공식** — Barron & Barrett (1996) *Management Science* 42(11):1515-1523 · Barron (1992) ROC · Stillwell (1981) RS

**생체 신호·사람**
- **심박 실측** — Mongin D, García Romero J, Alvero Cruz JR (2021) "Treadmill maximal exercise tests from the Exercise Physiology and Human Performance Lab of the University of Malaga" (v1.0.1), PhysioNet — https://doi.org/10.13026/7ezk-j442 · 라이선스 PhysioNet Contributor Review Health Data License 1.5.0 · 플랫폼 인용 Pollard TJ, et al. (2026) *Nature Health*
- **대사율** — Pandolf (1977) / NASA JSC EVA traverse 모델
- **VO2peak·지속가능 강도** — NTRS 20220014309 (ISS 승무원) · Coats 2003 / W′BAL
- **소모품** — 아폴로 15-17 PLSS · EMU 지속시간-작업률 NTRS 20150009506 · 아폴로 12 텔레메트리 NTRS 19720019460
- **피폭** — Hassler (2014) *Science* 10.1126/science.1244797 (Curiosity RAD) · Guo (2026) *JGR Planets* 10.1029/2026JE009704 (지형차폐)

상세 설계·근거는 [`docs/`](docs/) 참조. 라이선스: [MIT](LICENSE) — 코드·문서에 적용되며, 외부 데이터셋은 각 원본 라이선스를 따름.
