# MARSWALK 데이터 검증 현황 (갱신 2026-11-15)

> 기능별로 어느 데이터를 쓰는지, 받을 수 있는지, 어떻게 검증했는지, 투입한 값과 등급을 정리한 종합 문서임.
> 등급: 실측(실측, 실데이터), 논문(논문 공식이나 값), 추정(근거가 있고 교체 가능한 추정), 비데이터(공식, 기하, 설계처럼 데이터가 아닌 것)
> 앞부분은 이 문서에만 있는 기능별 요약이고, 뒷부분은 `docs/1_model_spec_handoff.md` 부터 `docs/12_api_data_spec.md` 까지를 번호 순서로 그대로 합친 사본임. 내용을 고칠 때는 docs 쪽을 먼저 고침.
> 상세: `README.md`, `docs/7_biosignature_design.md`, `docs/9_verification_status.md`

---

## 생명점수 검증 현황 (2026-11-15): S1, S2 실데이터, score 커버리지 100%

| 지표 | 입력 (실데이터) | 출처 | 상태 | 커버리지 |
|---|---|---|---|---|
| S1 함수/점토광물 | CRISM 광물 분류맵 | Zenodo 5575824 (Parente, Itoh, Saranathan) | 실측 | 2,488 / 3,067칸 (81.1%) |
| S2 퇴적, 델타 맥락 | USGS 지질맵 SIM 3464 | Sun & Stack 2020 (doi:10.3133/sim3464) | 실측 | 3,067 / 3,067칸 (100%) |
| S4 물 활동, S3 염류 | S1, S2 에 내재 / Jezero 에 드묾 | 없음 | 논문. 설계 완료, 미적용 | 없음 |
| S5 로버 근접 | 없음 | 없음 | 비데이터. 미투입 (유일) | 없음 |

- 생명점수(score)는 S1, S2 실데이터로 전 칸(100%)을 채움. 최소 / 평균 / 최대 = 25 / 42.7 / 100. 산출물은 `grid.js`, `grid.geojson` (칸 약 160m, 기지 5km 클립, 3,067칸).
- 방식은 투입된 지표만 재정규화하는 것임: `score = Σ(wᵢ·Sᵢ, 투입된 i) / Σ(wᵢ, 투입된 i) / 4 × 100`. 없는 값은 채우지 않고, 현재 분모는 w_S1 + w_S2 = 0.714 임. S3~S5 를 투입하면 다시 혼합됨.
- Jezero floor unit 의 S2 는 1 임. Perseverance 착륙 후 바닥이 화성암(Máaz, Séítah)으로 확인돼 퇴적 등급에서 낮춤. 델타 팬(Jezero fan)은 S2 4.
- 핀 4개(격자에서 읽은 값): 델타 전선 84 (S1=3, S2=4), Cheyava 25, Hawksbill 25, Séítah 29.5 (표시 30).
- S4 물 활동, S3 염류는 설계 완료, 미적용임. S4 는 S1(점토)과 S2(델타)가 둘 다 물로 형성, 퇴적된 지표라 이미 반영돼 있고(이중 계산 방지), S3 는 Jezero 에 염류가 드묾. 둘 다 ROC 가중치는 설계로 유지하고 투입하지 않음. 실제 미투입은 S5(로버 근접) 하나임. 경사와 교신은 DEM 실데이터로 전 칸에 반영돼 있음.

---

## A. 실데이터, 실측으로 검증한 것 (실측)

| 기능 | 데이터셋 | 받기 | 투입값 | 검증 |
|---|---|---|---|---|
| 심박 | PhysioNet 트레드밀, 검사 992건 | 원본을 받아 보정 (`scripts/calibrate_hr.py`). 원본은 저장소에 없음 | HR = 70.5 + 113.2·%VO2 | R²=0.77. 샘플 수는 문서에 따라 56만과 57만으로 다르게 남아 있음 (기록값) |
| 방사선 | Curiosity RAD (Hassler 2014) + 지형 차폐 (Guo 2026) | NASA PDS 에서 원본 공개 | 0.64 mSv/day, 차폐 약 20% | 화성 표면 직접 측정 |
| 지형 경사 | Jezero CTX DEM 20m (USGS) | 격자화 (`scripts/build_grid.py`) | 0.5 / 3.1 / 22.7° (5km 클립) | Jezero 지형과 부합 |
| 교신 음영 | 같은 CTX DEM (시선 판정) | 격자화 (안테나 15m) | clear 2,483칸, shadow 584칸 | 근거리에서는 영향이 작음 |
| 생명점수 S1 | CRISM 함수광물 (점토, 탄산염) | 격자화 | S1 0~4, 커버리지 81% | 점토, 탄산염은 생명 흔적 보존에 유력한 지표 |
| 생명점수 S2 | USGS SIM 3464 지질 (퇴적, 델타) | 격자화 | S2 0~4, 델타 전선이 핀 중 최고점 (84) | Jezero 바닥은 화성암이라 S2=1 (Perseverance 지상 확인) |
| 암석 피복 | THEMIS 열관성 (Zenodo 4931348, Edwards & Buz 2021) | 격자화 | rock 0~1, 이 격자에서는 0~0.32 | 열관성이 낮으면 모래 |
| 경로 탐색 | A* (경사, 암석 비용) | 동작 확인 | 델타 전선 22.7° → 11.2° (기록값) | 급경사 회피 확인 |
| POV 실사 | Mars 2020 raw image API | 받음 (`scripts/fetch_pov.py`) | 델타 sol 400대 | Perseverance 실촬영 |
| 지도 타일 | OpenPlanetary, Mars Trek | 스트리밍 | MOLA, THEMIS, HiRISE, CRISM | 없음 |
| 우주기상 | NASA DONKI API | 받음 | SPE, CME 이벤트 | 없음 |

## B. 논문 공식이나 값 (논문)

| 기능 | 출처 | 투입값 |
|---|---|---|
| 대사율 | Pandolf 1977 (NASA JSC EVA traverse) | M_W 식 |
| 생리 기준 | ISS 승무원 (NTRS 20220014309) | VO₂peak 37.5 / 42.1, 지속가능 35% |
| 지형계수 η | 레골리스를 느슨한 모래로 근사 (Soule & Goldman) | η = 2.0 |
| 소모품 (PLSS) | 아폴로 15~17 실측 (NTRS) | 산소, 냉각수 5.2 L, CO₂ 3.12 lb, 배터리 390 Wh |
| 피로, 체력 | W'BAL (Coats 2003) | 지속가능 강도 초과 시 소모, 이하에서 회복 |

## C. 격자 전처리: 실행과 확인 완료 (S1, S2 실데이터 반영)

- 입력: Jezero CTX DEM 20m/px (USGS, 약 90MB), CRISM 광물맵 (Zenodo 5575824), USGS 지질맵 SIM 3464, THEMIS 열관성 (Zenodo 4931348).
- 스크립트: `scripts/make_s2.py` (지질 폴리곤 → S2 래스터) → `scripts/build_grid.py` (DEM 경사, 교신 + S1 + S2 + rock → 격자).
- 산출: `make_s2.py` → `data/s2_jezero.tif` → `grid.js`. 3,067칸 (칸 약 160m, 기지 5km 클립). `window.GRID` 전역.
- 결과: 경사 0.5 / 3.1 / 22.7°, 교신 clear 2,483 / shadow 584, S1 2,488칸 (81.1%), S2 3,067칸 (100%), score 3,067칸 (100%, 25 / 42.7 / 100).
- 의미: S1 (CRISM), S2 (SIM 3464), 암석 피복 (THEMIS), A* 가 모두 채워지고 확인됨. 경사, 교신, 생명점수가 전부 실데이터임. S4 물 활동과 S3 염류는 설계 완료, 미적용이라 남은 것은 S5 (로버 근접) 투입임.
- 메모: Jezero 바닥은 Perseverance 지상 확인 결과 화성암(Máaz, Séítah)이라 S2 를 2 에서 1 로 낮췄고, 델타 팬만 고득점임.
- 생성: `python scripts/build_grid.py --dem jezero_dem.tif --crism zenodo_5575824/jezeroFinal.tif --geo data/s2_jezero.tif --geo-scored --rock zenodo_4931348/Jezero_Thermal_Inertia_v1.tiff --out grid.js --clip-km 5 --cell-px 8 --antenna-h 15`

## D. 데이터가 아닌 것: 공식, 기하, 설계 (비데이터)

| 항목 | 성격 | 근거 |
|---|---|---|
| 생명점수 가중치 | 데이터셋으로 만들 수 없음 (중요도) | 순위는 iMOST, Hartz & George. 숫자는 Barron ROC (0.457, 0.257, 0.157, 0.090, 0.040) |
| 복귀선의 2 나누기 | 기하 (왕복) | 가는 거리와 오는 거리가 같으므로 절반. 예비분 15% |
| 안전 게이트, 25° 차단 | 설계 선택 | 임계값은 로버 등반 한계 문헌으로 뒷받침할 수 있음 |
| 장비 무게 | 초기에는 대표값 (추정) | 이후 Apollo 문서값으로 채움 (`data/equipment.json`). 수트 질량은 수록하지 않음 |

데이터 자체가 존재할 수 없는 항목은 생명점수 가중치 하나임.

---

## 요약

대사율과 생리값은 NASA, ISS 문헌에서, 심박은 PhysioNet 검사 992건 실측 보정(R²=0.77)에서, 방사선은 Curiosity RAD 직접 측정에서, 소모품은 아폴로 실측에서 가져옴. 경사와 교신은 실제 Jezero CTX DEM 20m 를 격자화한 값임. 생명점수는 S1(CRISM 광물맵)과 S2(USGS 지질맵 SIM 3464) 실데이터로 전 칸(100%)을 채웠고, Jezero 바닥은 Perseverance 실측을 반영해 퇴적 점수를 낮춤. 가중치는 측정할 수 없는 중요도라 문헌으로 정한 순위와 Barron ROC 공식으로 계산함. 출처와 등급은 모두 문서에 적혀 있음.


---

# MARSWALK 모델 스펙 (2026-11-14 작성, 2026-11-15 심박식 갱신)

> 계산 모델별 정의, 공식, 입출력, 상수와 출처를 정리한 문서임. 참조 구현은 `marswalk_grid_demo.html` 의 `<script>` 부분임.
> 상수 출처 상세는 `docs/2_sources.md` 에 있음. UI 구성은 자유이고 아래 계산 로직만 같으면 됨.

---

## 0. 개요

화성 기지 대원의 도보 EVA 내비게이션에 쓰는 계산 6개를 다룸.

1. 대사율 (경사, 무게 → 에너지)
2. 산소 소모와 잔량
3. 복귀 반경 (walk-back)
4. 체력
5. 피폭
6. 생명점수 (지점 선택)

심박(§5, §11)은 대사율에서 파생되는 표시값임. 전부 입력을 받아 숫자를 내는 순수 함수이고 UI, 지도와 독립임.

---

## 1. 대사율 (Pandolf 방정식)

대원의 분당 에너지 소모를 계산함. 이후 모든 소모 계산의 출발점임.

```
G    = tan(경사도°) × 100                       # grade (%)
M_W  = 1.5·M + 2.0·(M+L)·(L/M)² + η·(M+L)·(1.5·v² + 0.35·v·G·g_mars)
```

- 입력: `M` 체중 kg, `L` 하중 kg, `v` 속도 m/s, 경사도 °
- 출력: `M_W` 대사율 (W)
- 상수: `η=2.0` (화성 레골리스를 모래로 근사), `g_mars=0.38`. 복귀 구간은 내리막으로 보고 G=0 으로 계산함(보수적 처리).
- 출처: NASA JSC EVA traverse 모델 (Pandolf 1977)

## 2. 산소 소모와 잔량

대사율을 산소 소모율로 바꾸고 탱크 잔량을 줄임.

```
O2_rate = M_W / 348                 # L/min  (산소 1L ≈ 20.9 kJ)
대사율_kcal_hr = M_W × 0.86
o2(t+Δ) = o2(t) − O2_rate · Δt      # 잔량, TANK=500 L (약 8h)
```

- 출력: `O2_rate` (L/min), `o2` (잔량 L)
- 데모 구현은 소모율에 `O2SCALE=0.80` 을 곱함. 복귀 완료 시 산소가 약 15% 남도록 맞춘 스케일이고 복귀선 계산에는 영향이 없음.

## 3. 복귀 반경 (walk-back), 왕복 기준

지금 남은 소모품으로 갔다가 돌아올 수 있는 최대 거리임. 안전 판단의 기준 지표임.

```
남은거리  = (o2 / TANK) × MAXWB          # 남은 총 보행거리(m). MAXWB=2000 (만충)
반경     = (남은거리 − MAXWB·RESERVE) / 2   # 2 로 나누는 것은 왕복. RESERVE=0.15 예비분
복귀판정: 기지까지_거리 ≥ 반경  →  복귀선 도달, 귀환
          > 반경×0.8          →  근접
          그 외               →  여유
```

- 2 로 나누는 이유: 반경만큼 나가면 같은 거리를 되돌아와야 함. 편도로 계산하면 귀환할 산소가 남지 않음. 그래서 나갈 수 있는 거리는 남은거리의 절반임.
- 예비분(RESERVE 15%): 역풍, 오르막, 실수에 대비한 안전 마진임. 도착 시 이만큼 남도록 함.
- 복귀 불능점(point of no return): 기지까지 거리가 반경과 같아지는 순간임. 넘기면 귀환할 수 없으므로 이 시점에 자동 귀환으로 전환함.
- 실시간 소모: 경사가 Pandolf 식으로 매 틱 소모율에 반영됨. 산소와 체력이 줄고 반경도 함께 줄어듦. 모두 §1, §2 에서 나오는 값이라 새 데이터가 필요 없음.
- 소모품이 줄면 반경이 줄어 먼 고득점 지점이 잠김. 산소가 90% 여도 멀면 잠기고, 20% 여도 가까우면 통과함.
- 계획 단계의 지점 잠금: 목적지까지 거리 D 에 대해 `2·D ≤ 남은거리 − MAXWB·RESERVE` 이면 왕복 가능.
- 다중 소모품 확장: 반경을 산소, 냉각수, CO2, 배터리 각각으로 계산한 뒤 최솟값을 씀(§10). 데이터는 `data/consumables.json`.
- 만충 시 반경은 (2000 − 300) / 2 = 850 m 임.

## 4. 체력 (W'BAL 개념)

지속가능 강도를 넘으면 체력이 줄고, 아래면 회복됨.

```
%VO2 = O2_rate / VO2abs             # VO2abs = VO2peak·M/1000 = 3.0 L/min
stam(t+Δ) = stam + (%VO2 > 0.35 ? −14·(%VO2−0.35) : +8·(0.35−%VO2)) · Δt
                                     # 0~100 범위로 제한
```

- 상수: `VO2peak=37.5` ml/kg/min (ISS 승무원), 지속가능 강도 `0.35` (30~40%)
- 출처: Coats 2003, W'BAL (critical power)

## 5. 심박

초기 설계식은 아래와 같았음.

```
HR = HR_rest + (HRmax − HR_rest)·%VO2  (+이벤트 보정)
```

- 초기 상수: `HR_rest=70`, `HRmax = 220 − 나이(34) = 186`
- 현재 구현은 PhysioNet 실측으로 보정한 §11 의 식을 씀. `HR_rest` 상수는 데모 코드에 없음.

## 6. 피폭 (방사선)

기준 선량에 위치(고도, 차폐) 보정을 곱해 시간에 따라 누적함.

```
altF = 1 + 고도_m / 5000            # 높을수록 증가
shF  = 1 − 0.2 · 차폐율             # 지형 차폐 최대 약 20% (RAD 실측)
dose(t+Δ) = dose + (RAD_DAY/1440)·altF·shF · Δt   # RAD_DAY=0.64 mSv/day
SPE 이벤트 시: dose += 1.2·shF
```

- 출처: Curiosity RAD (Hassler 2014), 지형 차폐 실측 (Guo 2026)
- 데모 구현 범위: `altF` 는 구현돼 있지 않음. `shF` 는 교신 음영 칸(`comm=shadow`)에서 0.8, 그 외 1.0 인 2단계임. SPE 는 `data/donki_sample.json` 의 활성 구간 동안 스텝마다 `spike_mSv·shF` 를 더하는 단순화 방식임.

## 7. 생명점수 (지점 선택)

어느 지점이 생명 흔적 탐사에 유력한지 나타내는 점수임. 지점 정렬과 선택에 쓰고, 안전 게이트가 항상 우선함. 상세는 `docs/7_biosignature_design.md` 에 있음.

```
생명점수(cell) = Σ wᵢ · Sᵢ                 # i = S1~S5, Σwᵢ = 1
화면추천(cell) = 안전게이트 × 생명점수        # 복귀선 밖, 급경사, 피폭 초과 = 잠금
```

- `Sᵢ`: 지점별 증거 강도 0~4 (SSTM, CoLD 척도). S1 점토광물, S2 퇴적 델타, S4 물 흔적, S3 염류, S5 로버 확인.
- `wᵢ`: 지표 순위에서 공식으로 계산함. 순위는 iMOST, Hartz & George 로 정하고 숫자는 Barron ROC, RS 공식으로 구함.
  - ROC 기본값: 0.457 / 0.257 / 0.157 / 0.090 / 0.040 (순위 1~5)
  - UI 에서는 숫자를 직접 입력하지 않고 순위를 재배열함(드래그). `data/weights.json` 참조.
- 실제 격자는 투입된 지표만 가중 재정규화해 0~100 으로 환산함. 현재 투입 지표는 S1, S2 임.
- 안전 우선: 생명점수가 100 이어도 복귀선 밖이면 추천하지 않음(회색 표시와 사유). 최종 go/no-go 는 우주인이 판단함.
- 출처: iMOST (Des Marais 2018), Hartz & George 2022, Barron & Barrett 1996, PersEIDS (NTRS 20230007488)

---

## 8. 데이터 입력 포맷

탐사 지점 (`data/spots.json`, `data/spots.js`):

```js
{ name, lat, lon, score, note, img }   // img = Perseverance 실사 URL
```

- 지도: OpenPlanetary, Mars Trek 타일 URL (Leaflet). 데모는 OpenPlanetary 화성 배경 타일을 씀.
- 우주기상: DONKI API(키 필요) 또는 과거 이벤트 1건 캐시(`data/donki_sample.json`)
- 격자(경사, 교신, 점수, 암석 피복): `grid.geojson`, 같은 내용의 전역판 `grid.js`. `scripts/build_grid.py` 산출물임.

---

## 9. 구현 메모

- 계산 6개는 순수 함수이므로 React 훅이나 유틸로 그대로 옮길 수 있음.
- 상태(산소, 체력, 피폭, 위치)는 Zustand 로 관리하는 구성을 가정함.
- `step()` 이 1틱 루프임. 데모는 `setInterval` 을 쓰고, 실제 앱은 requestAnimationFrame 이나 타이머를 쓰면 됨.
- 지도는 Leaflet(React-Leaflet), 차트는 Recharts 를 가정함.
- 참조 구현 `marswalk_grid_demo.html` 의 `<script>` 에 §1~§6 이 동작하는 형태로 들어 있음. §10 다중 소모품과 §6 의 `altF` 는 들어 있지 않음.

---

## 10. 다중 소모품 복귀선 (§3 확장, 설계)

복귀 한계를 산소 하나가 아니라 소모품 4종 중 가장 먼저 바닥나는 것으로 정하는 설계임. 용량 데이터는 `data/consumables.json` 에 있음. 초기 설계 때 참조한 `consumables.html` 은 이 저장소에 없고, 지도 데모에는 산소 기준만 구현돼 있음.

| 소모품 | 설계 용량(분) | 대사율 비례 |
|---|---|---|
| 산소 | 480 | 비례 |
| 냉각수 | 450 | 비례 (×1.05, 열부하) |
| CO₂ 스크러버 | 500 | 비례 (×0.95) |
| 배터리 | 420 | 비례 안 함 (일정) |

```
M0 = 273 W (기준 대사율 약 930 BTU/hr)
f  = M_W / M0
각 소모: remaining_i -= Δt × (비례이면 f, 아니면 1) × factor_i
복귀까지_분_i = remaining_i / (현재 소모율_i)
복귀 한계 = min(복귀까지_분_i)   ← walk-back 반경을 정함 (산소 단독이 아님)
```

- 고강도 작업에서는 냉각수와 산소가, 저강도 장시간 작업에서는 배터리가 먼저 바닥남.
- 표의 분 단위 용량과 계수는 설계 문서에만 있는 값임. `data/consumables.json` 에는 아폴로 15~17 PLSS 의 실제 용량(1430 psi, 5.2 L, 3.12 lb, 390 Wh)이 들어 있음.
- 출처: EMU PLSS (NTRS 20140009556), 아폴로 15~17 의 8h, 지속시간과 작업률 8h@930, 5h@1600 BTU/hr

---

## 11. 심박, 실측 보정값 (§5 갱신)

`HR = 70.5 + 113.2·%VO2` (PhysioNet 트레드밀 검사 992건 실측 보정, R²=0.77), 상한 HRmax 186.

- 참조 구현 `marswalk_grid_demo.html` 도 이 값(`HR_A=70.5`, `HR_B=113.2`, `HRMAX=186`)으로 동작함.
- 보정 스크립트는 `scripts/calibrate_hr.py` 임. PhysioNet 원본이 저장소에 없어 계수와 R² 는 기록값임.


---

# MARSWALK 모델 근거와 출처 (2026-11-15)

> 생체, 대사, 방사선, 지형 모델에 쓴 값의 출처를 모은 문서임.
> 값은 세 등급으로 나눔: 실측, 논문(공식이나 값), 추정(근거가 있고 교체 가능한 값).

---

## 0. 값의 종류

| 등급 | 뜻 | 예 |
|---|---|---|
| 실측 | 로버나 센서가 화성에서 직접 측정 | RAD 선량, 지형 피폭 차폐, 레골리스 물성 |
| 논문 | 발표된 방정식, 측정 평균 | Pandolf 식, VO₂peak, 지속가능 % |
| 추정 | 화성에서 직접 측정할 수 없어 논문 근거로 추정 | 지형계수 η, 산소통 용량 |

---

## 1. 대사율, Pandolf 방정식 (논문)

`M_W = 1.5·M + 2.0·(M+L)·(L/M)² + η·(M+L)·(1.5·v² + 0.35·v·G)`

- NASA JSC 가 EVA traverse 대사율 계산에 쓰는 식임(Mars Campaign Office 지원, JSC Rock Yard 현장 측정). ntrs.nasa.gov/citations/20240001423
- 원 방정식: Pandolf, Givoni, Goldman (1977) J Appl Physiol 43(4):577-81
- 와트 → kcal: ×0.01433 kcal/(W·min). 산소 1L ≈ 5 kcal (20.9 kJ)
- 구현(`scripts/calibrate_hr.py`, 데모)은 경사 항에 화성 중력비 `g_mars=0.38` 을 곱함.

## 2. 생리 기준값 (논문)

| 값 | 쓴 값 | 출처 |
|---|---|---|
| VO₂peak | 37.5(남) / 42.1(여) ml/kg/min | ISS 승무원 평균, ntrs.nasa.gov/citations/20220014309 |
| 지속가능 작업률 | VO₂peak 의 30~40% (35% 사용) | 같은 문헌 |
| 선발 평균 나이 | 34 → HRmax = 220 − 나이 | NASA 후보 평균, ntrs.nasa.gov/citations/20240001630 |
| 체중 | 80 kg | 추정. 대원 입력값(초기 문서 표기는 패드28), 데모 기본값 |
| 적재 하중 L (공구 + 시료통) | 20 kg 기본 (0~50 범위) | 논문. Apollo 지질공구 총질량 22.9~53.0 kg, Allton 1989 JSC-23454 |

적재 하중 L (`data/equipment.json`, 추정에서 논문 등급으로 올림)

Pandolf 식의 L 은 체중 외에 몸 밖으로 지거나 메는 하중(공구, 시료 수납통, 백팩/PLSS)임. 수트 착용 무게는 넣지 않음.

- 공구 캐리어 HTC 13.4 kg, 시료통 ALSRC(록박스, 빈 무게) 6.7 kg. Allton 1989, JSC-23454
- 임무별 지질공구 총질량(공구 + 용기): A11 22.9, A12 29.2, A14 34.1, A15 50.3, A16 53.0, A17 45.7 kg. 같은 카탈로그. 데모 기본 L 20 kg 은 Apollo 11 수준이고, 슬라이더 0~50 은 A11~A16 범위를 포함함.
- 참고 PLSS 질량: 제어부 포함 약 47 kg (104 lb), 본체 단독 약 38 kg (84 lb). NASA Apollo Lunar Surface Journal. PLSS 까지 L 에 넣는 고하중 시나리오용임.

## 3. 지형계수 η (추정에서 논문 등급으로 올림, 레골리스 실측 근거)

쓴 값: η ≈ 2.0 (범위 1.8~2.1)

- 화성 레골리스 실측은 느슨한 미세 모래에 해당함. Viking 밀도 1.0~1.3 g/cc, 점착 0~3.7 kPa (NTRS 20200003046). InSight 입자 0.06~0.2 mm, 점착 0~1 kPa (Delage 2017).
- 지형계수 표(Soule & Goldman 1972): 포장 1.0 부터 느슨한 모래 2.1 까지. 화성은 η 약 2.0 으로 둠.
- 리뷰: Richmond, Potter, Santee (2015)

## 4. 방사선 (대부분 실측)

| 값 | 쓴 값 | 출처 |
|---|---|---|
| 기준 선량 | 0.64 mSv/day | Curiosity RAD, Hassler 2014 Science |
| 지형 차폐 | 최대 약 19% 감소 | RAD 직접 관측, Guo 2026 JGR Planets |
| 고도, 대기 | 높을수록 증가 | RAD 4년 실측, Guo 2017 |

고도가 높을수록 피폭이 늘고 지형 차폐가 있으면 피폭이 줄어드는 방향은 둘 다 RAD 실측임(차폐 최대 약 19~24%). 데모는 차폐율 20% 를 씀.

## 5. 피로와 체력, W'BAL (critical power) (논문)

- 지속시간은 critical power 쌍곡선과 곡률상수 W' 로 설명됨. Coats 2003
- W'BAL: CP 초과 시 소모, 이하에서 회복, 고갈되면 탈진. 체력 모델이 이 구조를 따름.

## 6. 교체 요약 (초기 데모값 → 근거값)

| 항목 | 기존 | 교체 | 근거 |
|---|---|---|---|
| η | 1.5 | 2.0 | 레골리스를 모래로 근사 |
| 피폭 차폐 | 60% | 약 20% | RAD 실측 (Guo 2026) |
| 피로 | 선형 | W'BAL | Coats 2003 |
| 적재 하중 L | 대표값 20 kg | Apollo 실측 22.9~53.0 kg | Allton 1989 JSC-23454 |
| 암석 피복 rock | 없음 | THEMIS 열관성 실데이터 → 0~1 | Edwards & Buz 2021 (Zenodo 4931348) |
| 심박식 | 70 + 116·%VO₂ | 70.5 + 113.2·%VO₂ | PhysioNet 실측 회귀 (§9) |

## 7. 요약

대사율은 NASA 가 쓰는 Pandolf 방정식, 생리값은 ISS 승무원 실측, 방사선 지형 차폐는 Curiosity RAD 직접 관측(최대 19%), 지형계수는 Viking 과 InSight 의 레골리스 물성, 피로는 W' 모델에 근거함. 직접 측정할 수 없는 값(η, 체중)만 논문 근거 추정이고 전부 교체할 수 있음.

---

## 8. 참고문헌 (제목과 링크)

대사율 (Pandolf)

- Pandolf KB, Givoni B, Goldman RF (1977) "Predicting energy expenditure with loads while standing or walking very slowly." J Appl Physiol 43(4):577-581. https://journals.physiology.org/doi/10.1152/jappl.1977.43.4.577
- NASA JSC Crew State & Risk Model (IEEE EMBC 2024). NTRS 20240001423. https://ntrs.nasa.gov/citations/20240001423

생리 기준값

- ISS 승무원 EVA 유산소 능력. NTRS 20220014309. https://ntrs.nasa.gov/citations/20220014309
- "EVA Metabolic Rate Model: Metabolic Rate Estimated from Heart Rate". NTRS 20210024317. https://ntrs.nasa.gov/citations/20210024317
- Apollo EVA 대사율 234 kcal/hr. NTRS 19910001262. https://ntrs.nasa.gov/citations/19910001262
- 우주인 demographics (나이 34). NTRS 20240001630. https://ntrs.nasa.gov/citations/20240001630
- 산소 1L ≈ 5 kcal. NTRS 20120003917. https://ntrs.nasa.gov/citations/20120003917

방사선

- Hassler DM et al. (2014) "Mars' Surface Radiation Environment Measured with the Mars Science Laboratory's Curiosity Rover." Science 343. https://www.science.org/doi/10.1126/science.1244797
- Guo J et al. (2026) "Influence of Mars Topography on Radiation Dose Detected by MSL." JGR Planets. https://doi.org/10.1029/2026JE009704
- Guo J et al. (2017) "Dependence of the Martian radiation environment on atmospheric depth." JGR Planets. https://arxiv.org/abs/1712.06987
- Khaksarighiri S et al. (2023) "Zenith-Angle Dependence of the Downward Radiation Dose Rate on the Martian Surface." JGR Planets. https://doi.org/10.1029/2022JE007644

지형계수 η, 레골리스

- Soule RG, Goldman RF (1972) "Terrain coefficients for energy cost prediction." J Appl Physiol 32(5):706-708. https://journals.physiology.org/doi/abs/10.1152/jappl.1972.32.5.706
- Richmond PW, Potter AW, Santee WR (2015) "Terrain Factors for Predicting Walking and Load Carriage Energy Costs: Review and Refinement." JSHP 3(3). https://jhp-ojs-tamucc.tdl.org/jhp/article/view/67
- Mars soil simulants 리뷰 (Viking 물성). NTRS 20200003046. https://ntrs.nasa.gov/citations/20200003046
- Delage P et al. (2017) "Mechanical Properties of Martian Regolith Simulants." Space Sci Rev. https://doi.org/10.1007/s11214-017-0339-7

적재 하중 L (공구, 시료통, PLSS)

- Allton JH (1989) "Catalog of Apollo Lunar Surface Geological Sampling Tools and Containers." NASA JSC-23454 (LESC-26676), Lyndon B. Johnson Space Center. https://www.lpi.usra.edu/captem/lsac/alltonLunarToolCatalog.pdf (HTC 13.4 kg, ALSRC 6.7 kg, 임무별 공구 총질량 22.9~53.0 kg)
- NASA Apollo Lunar Surface Journal, Portable Life Support System (PLSS 제어부 포함 약 47 kg, 본체 약 38 kg). https://www.nasa.gov/wp-content/uploads/static/history/alsj/

생명점수 데이터셋 (S1 CRISM, S2 지질)

- S1 CRISM 광물맵: Parente M, Saranathan AM, Itoh Y, Tarnas JD, Seelos FP, Mustard JF, "Map of the dominant mineralogy over and around the Mars2020 landing ellipse with correspondent spectral signatures", Zenodo 5575824. https://doi.org/10.5281/zenodo.5575824 라이선스 CC-BY-4.0 (방법 논문: Itoh & Parente 2021, Saranathan & Parente 2021)
- S2 지질맵: Sun VZ & Stack KM (2020) "Geologic map of Jezero crater and the Nili Planum region, Mars", USGS SIM 3464. https://doi.org/10.3133/sim3464 라이선스: 미국 정부 저작물로 퍼블릭 도메인(출처 표기 권장)

암석 피복, 열관성 (rock 레이어, 안전과 A* 우회용)

- Edwards CS & Buz J (2021) "THEMIS-derived Thermal Inertia of Jezero Crater, Mars." Zenodo 4931348. https://doi.org/10.5281/zenodo.4931348 라이선스 CC-BY-4.0 (단위 J·m⁻²·K⁻¹·s⁻¹ᐟ², null=0)
- 기준값: 약 150 느슨한 모래, 350 굳은(indurated) 퇴적암, 1200 초과 결정질 화성암. rock(0~1) 은 2구간 선형 매핑임(150→350 이 0→0.5, 350→1200 이 0.5→1.0).
- 해석 근거: Mellon et al. 2000 (TES 열관성), Fergason et al. 2006 (THEMIS TI), Edwards & Buz 2021 (Jezero TI 맵)

체력 (W′BAL, critical power)

- Coats EM et al. (2003) "Intensity-dependent tolerance to exercise after attaining V̇O₂max in humans." J Appl Physiol 95(2):483-490. https://journals.physiology.org/doi/10.1152/japplphysiol.01064.2002

생명점수 프레임워크

- iMOST, MSR SSTM, Sephton et al., Conrad & Eigenbrode, Hartz & George (2022, Frontiers), ExoMars Biosignature Score (EBS)

---

## 9. 심박 모델, PhysioNet 실측 보정

- 데이터: PhysioNet 트레드밀 최대운동검사. 검사 992건, 약 57만 샘플 (심박, VO2, 속도). 원본이 저장소에 없어 건수와 샘플 수는 기록값임.
- 보정 결과: `HR = 70.5 + 113.2·%VO2` (R²=0.77)
- 비교: 보정 전 데모값(70 + 116·%VO2)과 계수 차이가 절편 0.5, 기울기 2.8 임. 데모는 보정식으로 교체함.
- HRmax(220 − 나이 = 186)를 상한으로 두고, %VO2 가 1 을 넘으면 지속 불가 플래그를 붙임.
- 데이터셋: Mongin D, García Romero J, Alvero Cruz JR (2021) "Treadmill maximal exercise tests from the Exercise Physiology and Human Performance Lab of the University of Malaga" (v1.0.1), PhysioNet, DOI 10.13026/7ezk-j442. physionet.org/content/treadmill-exercise-cardioresp/
  - 라이선스: PhysioNet Contributor Review Health Data License 1.5.0 (재배포 시 라이선스 표기 필수)
  - 원 논문: Mongin et al. (2021) *Research in Sports Medicine*, DOI 10.1080/15438627.2021.1954513
  - 플랫폼 표준 인용: Pollard TJ, et al. (2026) "PhysioNet as a global platform for biomedical research." *Nature Health*.
- 산출물: `data/synthetic_eva.json` (실측 보정 기반 EVA 시계열), 스크립트 `scripts/calibrate_hr.py`

---

## 10. 데이터셋 라이선스와 저작자 표기 (재배포 시 준수)

외부 데이터 출처별 라이선스와 저작자 표기임. Zenodo 두 건은 레코드의 `License` 필드를 확인했고(둘 다 CC-BY-4.0), PhysioNet 은 데이터셋 페이지의 라이선스를 따름.

| 데이터셋 | 라이선스 | 저작자 표기 |
|---|---|---|
| CRISM 광물맵 (Zenodo 5575824) | CC-BY-4.0 | Parente, Saranathan, Itoh, Tarnas, Seelos, Mustard (2021) |
| THEMIS 열관성 (Zenodo 4931348) | CC-BY-4.0 | Edwards & Buz (2021) |
| USGS SIM 3464 지질맵 | 미국 정부 저작물, 퍼블릭 도메인 | Sun & Stack (2020), USGS (출처 표기 권장) |
| Jezero DEM, Mars Trek 타일 | NASA, USGS. 퍼블릭 도메인 | NASA/JPL-Caltech, USGS Astrogeology |
| MSL RAD 선량 (PDS) | NASA. 퍼블릭 도메인 | NASA/JPL, Hassler et al. (2014) |
| DONKI 우주기상 | NASA Open Data. 퍼블릭 도메인 | NASA/CCMC |
| Perseverance raw 이미지 | NASA. 퍼블릭 도메인 | NASA/JPL-Caltech/ASU |
| OpenPlanetary 베이스맵 | 공개 타일 서비스 (기저 데이터는 NASA/USGS 퍼블릭 도메인) | OpenPlanetary, NASA/USGS |
| PhysioNet 트레드밀 심박 | PhysioNet Contributor Review Health Data License 1.5.0 | Mongin, García Romero, Alvero Cruz (2021) |
| Leaflet (데모 지도 라이브러리) | BSD-2-Clause | Leaflet 기여자 |

준수 요약

- CC-BY-4.0 (CRISM, THEMIS): 재사용 시 저작자, 출처, 라이선스 링크(https://creativecommons.org/licenses/by/4.0/)를 표기하고 변경 여부를 밝힘.
- NASA/USGS 퍼블릭 도메인: 저작권 제한이 없음. 관례에 따라 "courtesy NASA/JPL-Caltech", "USGS" 로 출처를 표기함.
- PhysioNet (Contributor Review Health Data License 1.5.0): 데이터셋을 재배포할 때 라이선스 전문과 DOI 를 함께 둠. 표준 인용은 Pollard et al. (2026, *Nature Health*)와 데이터셋 저자(Mongin et al. 2021)임. 이 저장소에는 PhysioNet 원본이 들어 있지 않음.
- 이 저장소의 격자 산출물(`grid.geojson`, `grid.js`, `data/s2_jezero.tif`)은 위 소스를 가공한 2차 산출물임. 배포할 때 원 소스의 라이선스(특히 CC-BY 저작자 표기)를 따름.


---

# MARSWALK 데이터 레퍼런스 (2026-11-14 작성, 2026-11-15 갱신)

> 데이터별 링크, 쓰는 기능, 가져오는 방법, 저장 방식을 정리함. 외부 NASA 데이터는 6계열임. 챌린지 요건인 데이터 3종 이상에 대해 5종을 씀.

## 저장 패턴 4가지

- A. 스트리밍(저장 없음): 베이스맵, 과학 타일. Leaflet 이 타일 서버에서 실시간으로 받음.
- B. 격자 GeoJSON(전처리): 경사, 암석 피복, 생명점수. Jezero 격자에 값을 넣어 둠.
- C. 라이브 또는 캐시 JSON: DONKI. 라이브 호출 또는 과거 1건 캐시.
- D. 상수와 URL: RAD, POV, 생체. 코드나 JSON 에 고정값으로 둠.

보기용 레이어(A)와 계산용 레이어(B)를 섞지 않음.

## 외부 NASA 데이터 6계열

1. 지형, 경사: Jezero CTX DEM 20m (USGS Astrogeology). `scripts/build_grid.py` 가 DEM 기울기로 경사를 계산함. 초기 계획은 Trek(https://trek.nasa.gov/mars/)의 MOLA+HRSC DEM 과 `gdaldem slope` 였음. (저장 B)
2. 암석 피복: THEMIS 열관성 실데이터(Zenodo 4931348, Edwards & Buz 2021). `build_grid.py --rock` 으로 rock(0~1) 을 격자에 넣음. 열관성이 낮으면 모래, 높으면 바위. A* 가 바위밭을 우회하는 비용으로 씀. (저장 B)
3. 광학 베이스맵: Trek, OpenPlanetary https://www.openplanetary.org/opmbasemaps (저장 A)
4. 과학, 생명, 물 흔적: CRISM 광물맵(Zenodo 5575824), USGS SIM 3464 https://pubs.usgs.gov/publication/sim3464 를 격자로 변환함. 초기 계획의 Trek CRISM, 염류 타일은 보기용임. (저장 A+B)
5. 우주기상, 방사선: DONKI https://api.nasa.gov/, RAD (Hassler 2014) (저장 C+D)
6. POV 실사: https://mars.nasa.gov/mars2020/multimedia/raw-images/ 와 Raw API (키 불필요) (저장 D)

## 데이터를 쓰지 않는 기능 (로직, 입력, 기기, 시뮬레이션)

- 산소와 복귀 모델, 위치와 방위 계산, 사용자 입력과 설정, 기기(음성, 버튼, 카메라), 시뮬레이션(버디, 통신)

## 실데이터가 없어 근사나 시뮬레이션으로 정한 6항목

1. 통신 음영: DEM 시선(LOS) 근사
2. 심박: 실시간 피드는 시뮬레이션. 심박과 %VO₂ 의 관계식은 이후 PhysioNet 트레드밀 실측으로 보정함(`docs/2_sources.md` §9)
3. POV 조인: 노두 사전 매칭
4. 바위 단위: 해결됨. THEMIS 열관성(Zenodo 4931348)으로 rock(0~1) 을 실데이터화함. 초기 계획이던 HiRISE 디지타이즈는 필요 없어져 쓰지 않음
5. 초국지 지형: HiRISE 고배율 확대
6. DONKI 타이밍: 이벤트 시각이 지구 기준이라는 점을 각주로 밝힘

## 챌린지 요건 충족

데이터 3종 이상 요건에 대해 5종을 써서 충족함. 데이터가 없어 구현하지 못한 기능은 없음.

## 생체 데이터

우주인의 실시간 생체 피드는 공개된 것이 없음. 그래서 NASA 논문 수치를 코드 상수로 넣음.

- 공식과 값은 `docs/2_sources.md` 참고. 심박의 실시간 값은 시뮬레이션이고, 식의 계수는 PhysioNet 공개 데이터로 보정함.

## 공식 챌린지 리소스 대조

- 공식 리소스에 포함: Mars Trek, USGS, Perseverance
- 추가로 쓴 것: OpenPlanetary, DONKI


---

# MARSWALK 결정 로그 (2026-11-14)

> NASA Space Apps Challenge 2026, Challenge 10 (Interplanetary Survival Guide: Martian Map), 팀 team-navis

## 1. 정체성

화성 기지 대원용 EVA 도보 내비게이션임. 기지에서 계획하고(패드) 현장에서 걸음(HUD). 목표는 Jezero, Neretva 삼각주에서 생명 흔적(biosignature) 샘플을 확보하는 것임.

## 2. 사람을 화성에 보내는 이유

로봇 탐사가 수십 년 이어졌지만 현장의 실시간 판단과 과학 활동은 사람이 맡음. MARSWALK 는 그 대원이 더 오래, 더 멀리, 더 안전하게 과학 활동을 하도록 돕는 도구임. walk-back 은 과학 활동 시간을 지키는 장치로 둠.

## 3. 관제는 화성 표면 기지의 버디

- 지구 관제: 채택하지 않음. 편도 최대 약 22분, 왕복 약 44분이라 실시간 대응이 불가능함.
- 화성 궤도: 채택하지 않음. 패스 때만 교신할 수 있어 연속 감시가 불가능함.
- 표면 버디: 채택. 같은 지표에 있어 지연이 거의 없고 계속 연결됨.

## 4. 양면 구조

- 패드(관제, 계획): 지도 4층, 경로, 산소 예산, 안전 링, 생체, 우주기상, 과학 목표, 교신
- HUD(현장, 최소): 산소, 시간과 방향, 복귀 데드라인, 경보, 교신 상태
- 기준: 지금 보지 않으면 생명이 위험한 정보만 HUD 에 둠.

## 5. 데이터 4층과 산소

경사, 지질, 방사선, 열. 실제 NASA 데이터이고 필수 3층보다 많은 4층임. 산소는 walk-back 계산의 입력임. 필수 요건 5개 중 5개를 충족함.

## 6. HUD 유형

컴바이너식 축약 HUD 를 현실적인 기본안으로, AR HUD 를 장기 구상으로 둠. 헬멧은 눈과 유리 사이가 약 10cm 라 윈드실드식은 쓸 수 없음.

## 7. 동적 안전 반경 (turn-back line)

산소, 지형, 폭풍, 통신 중 가장 제약이 큰 값으로 반경을 자동 계산하고, 걸을수록 반경이 줄어듦.

- 3단계 표시: 자유(녹색), 주의(황색), 통제선(적색)
- HUD 는 복귀선까지 남은 값을 표시하고, 패드는 반경을 조절함.
- 지도 데모(`marswalk_grid_demo.html`)는 산소 기준 반경만 구현함.


---

# MARSWALK 페이지별 데이터 검증 목록 (2026-11-14 작성, 2026-11-15 갱신)

> 패드 각 페이지의 요소, 데이터와 모델, 파일, 근거, 상태를 표로 정리함. 페이지 구성은 앱 설계 기준이고 이 저장소에는 지도 데모만 구현돼 있음.
> 상태 표기: 실측(실측, 검증), 논문, 계산, 입력(입력 또는 UI), 근사(근사 또는 시뮬레이션)

## 홈

| 요소 | 데이터 | 파일 | 근거 | 상태 |
|---|---|---|---|---|
| 대원 2인 상태 | 생체 시뮬레이션 | synthetic_eva.json | PhysioNet 검사 992건 실측 | 실측 |
| 계획 시작 | UI | 없음 | 없음 | 입력 |

## 1. 지점 고르기

| 요소 | 데이터 | 파일 | 근거 | 상태 |
|---|---|---|---|---|
| 지도, 레이어 5종 | 타일, 격자 | layers.json, grid.geojson | OpenPlanetary, CTX DEM | 실측 (경사 격자 산출 완료) |
| 가중치 3종 | 프레임워크 | weights.json | iMOST, SSTM | 논문 |
| 후보 순위 | 생명점수 | weights.json + spots.json | SSTM 가중합 | 논문 |
| 근거 등급 | 출처 메타 | layers.json | CRISM 은 궤도, Perseverance 는 로버 | 실측 |
| 복귀 불가 표기 | walk-back | consumables.json | Pandolf + PLSS | 실측 |
| 지점 영상 | POV | spots.json | Perseverance 실사 | 실측 |

## 2. 계획 세우기

| 요소 | 데이터 | 파일 | 근거 | 상태 |
|---|---|---|---|---|
| 우주기상 | DONKI | donki_sample.json | api.nasa.gov/DONKI | 실측 |
| 적재 선택 | 장비 무게 | equipment.json | Apollo 문서값 (Allton 1989), 입력 | 입력 |
| 산소 예산, 복귀 시각 | 모델 | consumables.json | Pandolf + PLSS (아폴로) | 논문 |

## 3. 경로 미리보기

| 요소 | 데이터 | 파일 | 근거 | 상태 |
|---|---|---|---|---|
| 장애물, 통과 불가 | DEM 경사 + 암석 피복 | grid.geojson, layers.json | CTX DEM 20m, THEMIS 열관성. 경사 임계 25° (초기 문서에는 15~20° 로 적혀 있었음) | 실측 (격자 산출 완료) |
| 복귀 불가 루트 | walk-back | consumables.json | Pandolf + PLSS | 실측 |

## 4. 출발 확인

| 요소 | 데이터 | 파일 | 근거 | 상태 |
|---|---|---|---|---|
| 점검, 비상 분기, HUD 전송 | UI, 운영 | 없음 | 없음 | 입력 |

## 5. 관제

| 요소 | 데이터 | 파일 | 근거 | 상태 |
|---|---|---|---|---|
| 대원 상태 (산소, 심박) | 모델 | synthetic_eva.json, crew_spec.json | PhysioNet 실측 R²=0.77 | 실측 |
| 소모율 감시 | 소모품 | consumables.json | 아폴로 PLSS | 논문 |

## 6. 경보 대응

| 요소 | 데이터 | 파일 | 근거 | 상태 |
|---|---|---|---|---|
| 경보 내용 | DONKI | donki_sample.json | api.nasa.gov | 실측 |
| 선택지 피폭 (X선 환산) | RAD | radiation.json | Hassler 2014 Science | 실측 |

## 7. 리포트

| 요소 | 데이터 | 파일 | 근거 | 상태 |
|---|---|---|---|---|
| 시료 핀 | POV | spots.json | Perseverance | 실측 |
| 누적 피폭 | RAD | radiation.json | Hassler 2014 + Guo 2026 | 실측 |

## 설정

| 요소 | 데이터 | 파일 | 근거 | 상태 |
|---|---|---|---|---|
| 대원 제원 | 입력 | crew_spec.json | NTRS, PhysioNet | 실측 |
| 장비 무게 | 입력 | equipment.json | Apollo 문서값 (Allton 1989) | 입력 |

---

## 데이터 파일 목록 (data/)

| 파일 | 내용 | 근거 |
|---|---|---|
| spots.json, spots.js | 탐사 지점, POV | Perseverance |
| weights.json | 생명점수 가중치 | iMOST, SSTM |
| layers.json | 지도 레이어 정의 (과학 5종, 안전 5종) | CRISM, USGS, THEMIS, RAD |
| consumables.json | EVA 소모품 4종 | 아폴로 PLSS |
| radiation.json | 피폭 상수 | RAD, Hassler, Guo |
| crew_spec.json | 대원 제원 | NTRS, PhysioNet |
| equipment.json | 장비 무게 | Apollo 문서값 (Allton 1989, NASA ALSJ) |
| donki_sample.json | 우주기상 | DONKI |
| synthetic_eva.json | 실측 보정 생체 시계열 | PhysioNet 검사 992건 |
| pov_candidates.json | Perseverance raw 이미지 후보 목록 | Mars 2020 raw API |
| s2_jezero.tif | S2 래스터 (SIM 3464 재코딩) | USGS SIM 3464 |

## 격자 전처리 상태

- 초기 작성 시점에는 경사 격자(DEM)와 생명점수 격자(CRISM)가 없어 슬라이더와 점수 근사를 썼음.
- 현재는 `scripts/build_grid.py` 로 산출한 `grid.geojson`, `grid.js` 가 저장소 루트에 있음. 3,067칸, 칸 약 160m.


---

# MARSWALK 원본 데이터 다운로드 (2026-11-14 작성, 2026-11-15 갱신)

> 이 저장소가 쓴 실측, 공개 데이터의 원본을 받을 수 있는 링크임. 대용량 원본은 `.gitignore` 로 제외돼 저장소에 들어 있지 않음. 재현할 때 두는 경로는 루트 `README.md` 의 데이터 절에 있음.

## 심박, PhysioNet (검사 992건 실측)

- 페이지: https://physionet.org/content/treadmill-exercise-cardioresp/
- AWS: `aws s3 sync --no-sign-request s3://physionet-open/treadmill-exercise-cardioresp/ ./physionet_data/`
- DOI: 10.13026/7ezk-j442. 필드: time, Speed, HR, VO2, VCO2, RR, VE
- 쓰임: `scripts/calibrate_hr.py`. 재현 시 `physionet_data/` 에 둠.

## 방사선 RAD, NASA PDS (화성 표면 실측 선량)

- PDS-PPI: https://pds-ppi.igpp.ucla.edu/data/MSL-M-RAD-3-RDR-V1.0/
- 검색: https://search-pdsppi.igpp.ucla.edu/search/view/?id=pds://PPI/MSL-M-RAD-3-RDR-V1.0/DATA
- SPDF (cdaweb): https://cdaweb.gsfc.nasa.gov/ 에서 MSL, MSL_RAD_OBS-L2
- 논문: Hassler 2014 Science DOI 10.1126/science.1244797
- 이 저장소는 RAD 원본을 내려받아 처리하지 않고 논문의 대표값(0.64 mSv/day)을 `data/radiation.json` 에 상수로 둠.

## POV 실사, Perseverance (Mars 2020 raw)

- 갤러리: https://mars.nasa.gov/mars2020/multimedia/raw-images/
- API: https://mars.nasa.gov/rss/api/?feed=raw_images&category=mars2020&feedtype=json
- 키 불필요, 퍼블릭 도메인
- 쓰임: `scripts/fetch_pov.py`, `data/pov_candidates.json`

## 지도, 지형, 광물, Mars Trek

- 포털: https://trek.nasa.gov/mars/
- 제품: MOLA, HRSC (지형), THEMIS (열), Viking, CTX, HiRISE (광학), CRISM (함수광물)
- 격자 산출에 실제로 쓴 DEM 은 Jezero CTX DEM 20m (USGS Astrogeology, 약 90MB)이고 재현 시 `jezero_dem.tif` 로 둠.

## 광물맵 (S1), Zenodo 5575824

- 페이지: https://doi.org/10.5281/zenodo.5575824 (Parente, Itoh, Saranathan, Jezero crater mineral map, CC-BY-4.0)
- 쓰임: `build_grid.py --crism`. 재현 시 `zenodo_5575824/jezeroFinal.tif` 로 둠.

## 우주기상, DONKI

- API: https://api.nasa.gov/DONKI/ (DEMO_KEY 또는 무료 키)
- SEP, FLR, notifications

## 지질 (S2), USGS

- 허브: https://astrogeology-usgs.hub.arcgis.com/pages/interactive-maps-mars
- Jezero: SIM 3464 https://pubs.usgs.gov/publication/sim3464
- 쓰임: `scripts/make_s2.py`. 재현 시 `sim3464_extract/sim3464_JezeroNili_FINAL/Geodatabase/Nili.gdb` 로 둠. 재코딩 결과 `data/s2_jezero.tif` 는 저장소에 들어 있음.

## 암석 피복 (열관성), Zenodo 4931348

- 페이지: https://doi.org/10.5281/zenodo.4931348 (Edwards & Buz 2021, "THEMIS-derived Thermal Inertia of Jezero")
- 파일: `Jezero_Thermal_Inertia_v1.tiff` (1.72MB, GeoTIFF, 단위 J·m⁻²·K⁻¹·s⁻¹ᐟ², null=0, MD5 53fec7c990a90629e98c871a7a0da474)
- 받기: `curl -L -o Jezero_Thermal_Inertia_v1.tiff https://zenodo.org/api/records/4931348/files/Jezero_Thermal_Inertia_v1.tiff/content`
- 쓰임: `build_grid.py --rock` 으로 rock(0~1) 격자를 만듦(A* 의 바위밭 우회 비용). 재현 시 `zenodo_4931348/` 에 둠.

---

## 논문값 (원본이 논문이나 보고서인 것)

- Pandolf 1977: journals.physiology.org/doi/10.1152/jappl.1977.43.4.577
- 아폴로 PLSS 소모품: NTRS 19720019460, 20150009506
- 레골리스: Delage 2017 DOI 10.1007/s11214-017-0339-7, NTRS 20200003046
- 지형계수: Soule & Goldman 1972, Richmond 2015
- 장비 무게: Allton 1989 JSC-23454, NASA Apollo Lunar Surface Journal (`data/equipment.json`)

## 모델링 가정 (원본 데이터 없음, 근거에 따른 설계값이고 조정 가능)

- 생명점수 가중치: 지표 순위는 문헌 프레임워크로 정하고 숫자는 ROC 공식으로 계산함. 순위는 사용자가 재배열할 수 있음.
- 방사선 장소 보정식: 방향은 실측과 일치하고 식은 근사임.
- 기본 적재 하중 20 kg, 체중 80 kg: 대표값임.


---

# MARSWALK 생명점수(Biosignature Score) 상세 설계 (갱신 2026-11-15)

> 목적지 선정에 쓰는 과학 점수의 설계 문서임. 지표 순위는 문헌 프레임워크로 정하고, 가중치 숫자는 공식으로 계산하며, 안전은 별도 게이트가 우선함.
> 점수 정의는 데이터(JSON)로 분리돼 있음: `data/weights.json`, `data/layers.json`.

---

## 구현 현황 (2026-11-15): S1, S2 실데이터 적용, score 커버리지 100%

| 지표 | 입력 레이어 | 상태 | 커버리지 |
|---|---|---|---|
| S1 함수/점토광물 | CRISM 광물맵 (Zenodo 5575824, Parente, Itoh, Saranathan) | 실데이터 투입 | 2,488 / 3,067칸 (81.1%) |
| S2 퇴적, 델타 맥락 | USGS 지질맵 SIM 3464 (Sun & Stack 2020) | 실데이터 투입 | 3,067 / 3,067칸 (100%) |
| S3 보존성 염류 | (Jezero 에 드묾) | 설계 완료, 미적용 | 해당 적음 |
| S4 물 활동 | (S1, S2 에 내재) | 설계 완료, 미적용 | 이미 반영 |
| S5 로버 현장 근접 | 없음 | 미투입 | 없음 |

> 번호 규약: 코드(`build_grid.py` 의 `ROC_DEFAULT`)와 가중치 기준으로 S4 가 물 활동(순위 3, ROC 0.157), S3 가 보존성 염류(순위 4, ROC 0.090)임. ROC 는 순위로 가중치가 정해지므로 번호와 순위가 다름.

- S4 물 활동, 설계 완료 미적용(이미 반영): S1(점토, 함수광물)과 S2(델타, 퇴적)가 모두 물로 형성, 퇴적된 지표임. 과거 액체 물 활동은 S1, S2 에 이미 들어 있어 별도 레이어를 더하면 같은 신호를 두 번 세게 됨. 루브릭과 가중치(순위 3, ROC 0.157)는 설계로 유지하고 Jezero 에는 투입하지 않음.
- S3 보존성 염류, 설계 완료 미적용(해당 적음): 황산염, 염화물 같은 보존성 염류는 iMOST 보존광물이지만 Jezero 는 염류가 드물어(주 신호가 점토, 탄산염, 델타 퇴적) 변별력이 낮음. 루브릭과 가중치(순위 4, ROC 0.090)는 설계로 유지하고 투입하지 않음.
- 생명점수는 S1, S2 실데이터로 전 칸(100%)을 채움. 격자 산출물은 `grid.js`, `grid.geojson` (칸 약 160m, 기지 5km 클립, 3,067칸).
- score 최소 / 평균 / 최대 = 25 / 42.7 / 100. 델타 팬과 점토가 겹치는 칸이 80~100 점대를 이룸.
- 점수는 투입된 지표만 재정규화함: `score = Σ(wᵢ·Sᵢ, 투입된 i) / Σ(wᵢ, 투입된 i) / 4 × 100`. 현재 분모는 w_S1 + w_S2 = 0.457 + 0.257 = 0.714. S3~S5 가 들어오면 다시 혼합됨. 없는 값은 채우지 않음.
- Jezero floor unit 의 S2 는 1 임(호저 저지). Perseverance 착륙 후 바닥이 화성암(Máaz, Séítah)으로 확인돼 퇴적 등급에서 낮춤. 델타 팬(Jezero fan 1, 2, Nili Planum fan)은 S2 4.
- 미투입으로 남은 지표는 S5(로버 근접)임. 안전 레이어(경사, 교신)는 DEM 실데이터로 반영돼 있음.

생성 명령(저장소 루트에서 실행):

```
python scripts/build_grid.py --dem jezero_dem.tif \
  --crism zenodo_5575824/jezeroFinal.tif \
  --geo data/s2_jezero.tif --geo-scored \
  --rock zenodo_4931348/Jezero_Thermal_Inertia_v1.tiff \
  --out grid.js --clip-km 5 --cell-px 8 --antenna-h 15
```

S2 래스터는 `scripts/make_s2.py` 가 SIM 3464 의 GeoUnits_v1 폴리곤을 유닛별 S2(0~4)로 바꿔 `data/s2_jezero.tif` 로 만듦.

---

## 0. 요약

1. 생명점수 = Σ wᵢ·Sᵢ. 지점마다 지표 5개(Sᵢ, 0~4)를 가중합함.
2. 가중치 wᵢ 는 직접 고르지 않음. 지표 순위만 문헌으로 정하고 공식(ROC, RS)이 숫자를 계산함. 숫자의 근거가 공식으로 남음.
3. 생명점수는 보조 지표임. 안전(복귀선, 경사, 피폭)이 별도 게이트로 추천을 잠금. 최종 판단은 우주인이 하고 안전이 우선함.

---

## 1. 점수 공식

```
생명점수(cell) = Σ wᵢ · Sᵢ(cell)      # i = S1..S5
0~100 환산      = (Σ wᵢ·Sᵢ) / 4 · 100   # Sᵢ 최대 4, Σwᵢ=1 → 최대 4
```

- Sᵢ: 지점별 증거 강도(0~4). 그 칸에서 지표가 얼마나 강하게 나타나는지를 뜻함.
- wᵢ: 지표 중요도(합 1). 그 지표가 일반적으로 얼마나 중요한지를 뜻함.
- 두 역할을 나눔. 로버 현장 확인은 신뢰도가 가장 높으므로 있으면 Sᵢ=4 로 반영하고, 커버리지가 좁으므로 가중치 wᵢ 는 낮게 둠.
- 실제 격자 계산은 구현 현황의 재정규화식을 씀. 지표가 하나도 없는 칸은 null 임.

### Sᵢ 0~4 척도 (SSTM, CoLD 방식 단계)

| 점수 | 뜻 |
|---|---|
| 0 | 신호 없음 |
| 1 | 약한 간접 정황 |
| 2 | 궤도 관측 암시 |
| 3 | 강한 궤도, 분광 신호 |
| 4 | 로버 현장 확인 |

근거: MSR SSTM(증거 추적 행렬), CoLD scale(Confidence of Life Detection, Green et al. 2021 *Nature*)의 증거 단계 개념.

구현된 S1, S2 루브릭은 궤도 자료만으로 4점을 줌(아래 채점 루브릭). 위 척도의 4점 정의(로버 현장 확인)와 다르며, 로버 확인 여부는 S5 로 따로 다루는 구조임.

---

## 2. 지표 5개와 순위의 근거

순위 기준은 iMOST 보존광물 우선순위, Hartz & George (2022) 신뢰도와 검출도, Mars 2020 SDT 생체신호 유형임.

| 순위 | 지표 | 입력 레이어 | 상태 | 순위 이유 | 근거 |
|---|---|---|---|---|---|
| 1 | 함수/점토광물 | CRISM 광물맵 (Zenodo 5575824) | 실데이터 투입 | 점토는 유기물 보존에 가장 유리한 매질임. iMOST 가 보존에 유리한 퇴적물로 명시함. Jezero 델타에서 수십억 년 보존이 확인됨 | iMOST (Des Marais 2018), McMahon 2018, Hickman-Lewis 2025 |
| 2 | 퇴적, 델타 맥락 | 지질 SIM 3464 (Sun & Stack 2020) | 실데이터 투입 | 세립 퇴적물(이암, 델타)은 유기탄소 매장과 보존에 유리함. Gale 이암에서 점토와 유기물이 함께 검출됨 | Broz 2020, Gale SAM |
| 3 | 물 활동 흔적 | (S1, S2 에 내재) | 설계 완료, 미적용 | 과거 액체 물은 거주가능성의 전제임. 다만 S1 점토와 S2 델타가 모두 물로 형성, 퇴적된 지표라 이미 반영돼 있음. 이중 계산을 피하려고 따로 넣지 않음 | iMOST 수성 맥락, MSR SSTM |
| 4 | 보존성 염류 | THEMIS, CRISM 염류 | 설계 완료, 미적용 | 황산염, 탄산염은 iMOST 보존광물이지만 Jezero 는 염류가 드물어 변별력이 낮음. 설계만 유지함 | iMOST, Osterloo 2008 |
| 5 | 로버 현장 근접 | Perseverance, MSL | 미투입 | 직접 검출은 신뢰도가 가장 높지만 커버 범위가 좁아 가산 요소로 둠 | Mars 2020, CoLD (Green 2021) |

### S1, S2 채점 루브릭 (구현된 부분)

S1: CRISM 광물 → S1(0~4). 범례의 최근접 색으로 분류하고 칸 범위 안의 최빈 광물을 씀. 검정(미식별)과 흰색(배경)은 제외함.

| S1 | 광물 (CRISM 범례) | 근거 |
|---|---|---|
| 4 | 탄산염, 점토(스멕타이트, 카올리나이트), 함수실리카 | iMOST 1순위 보존광물 |
| 3 | 올리빈 + 점토 혼합(기타 수화) | 점토 신호가 있으나 혼합 |
| 1 | 올리빈, 휘석(현무암질) | 수화 광물 아님 |

S2: SIM 3464 지질 유닛 → S2(0~4). 유닛 폴리곤을 래스터화하고 칸 범위 평균을 씀.

| S2 | 지질 유닛 | 근거 |
|---|---|---|
| 4 | Jezero fan 1, 2, Nili Planum fan (삼각주 퇴적) | Broz 2020: 세립 델타, 호성 퇴적물이 유기물 보존에 가장 유리 |
| 3 | Smooth unit, undivided (평활 퇴적평원) | 세립일 가능성 |
| 1 | Jezero floor (호저), etched, Nili Planum, 풍성 사구 | floor 는 화성암(Máaz, Séítah, Perseverance 실측)이라 퇴적이 아님 |
| 0 | Rugged bright, Crater rim, ejecta, interior | 충돌 기원, 노출암 |

문헌 링크 전체는 `docs/2_sources.md` §8 에 있음.

---

## 3. 가중치: 순위에서 숫자를 계산하는 방식

0.30, 0.25, 0.20 같은 숫자를 직접 고르면 그 숫자의 근거를 댈 수 없음. 그래서 지표의 순위만 문헌으로 정하고, 순위를 숫자로 바꾸는 일은 공개된 MCDA 공식에 맡김.

> 출처: Barron & Barrett (1996) *Management Science* 42(11):1515-1523. 사람에게서 정확한 가중치를 직접 얻는 것은 존재하지 않는 정밀도를 요구하는 일이므로, 순위만 받고 대리 가중치(surrogate weight)로 변환한다는 내용임.

### 두 공식

| 공식 | 식 | 특징 |
|---|---|---|
| ROC (Rank Order Centroid, Barron 1992) | wᵢ = (1/N)·Σ_{k=i..N}(1/k) | 상위 지표를 강하게 강조 |
| RS (Rank Sum, Stillwell 1981) | wᵢ = (N+1−i)/Σ | 완만하게 차등 |

### N=5 계산 결과 (합 1.0 확인)

| 순위 | ROC | RS |
|---|---|---|
| 1 | 0.457 | 0.333 |
| 2 | 0.257 | 0.267 |
| 3 | 0.157 | 0.200 |
| 4 | 0.090 | 0.133 |
| 5 | 0.040 | 0.067 |

- 기본은 ROC(과학권장)임. 상위 지표(점토)를 강조하는 점이 보존 과학의 우선순위와 맞음.
- 초기 데모값 0.30 / 0.25 / 0.20 / 0.15 / 0.10 은 RS 와 거의 같음. RS 도 대안으로 쓸 수 있음.
- 프리셋은 순위를 바꾸는 방식임(물추적, 검증우선). 슬라이더로 숫자를 조정하지 않고 순위를 재배열하면 공식이 다시 계산함.
- 계산은 `scripts/gen_biosignature.py` 가 하고 결과는 `data/weights.json` 에 있음.

---

## 4. 레이어에서 점수까지의 흐름

```
[과학 레이어]  CRISM, 지질, THEMIS, 로버
     │  각 칸에서 레이어값 → Sᵢ(0~4) 루브릭 채점
     ▼
  생명점수 = Σ wᵢ·Sᵢ  →  0~100  →  히트맵
     │
     ▼
[안전 레이어]  복귀선, 경사, 피폭, 통신  →  게이트
     │
     ▼
화면 추천 = 게이트 × 생명점수
```

- 전처리: Jezero CTX DEM 20m, CRISM, 지질, THEMIS 열관성을 공통 격자(칸 약 160m, 3,067칸)로 리샘플해 루트의 `grid.geojson` 으로 만듦. 칸 속성은 `slope_deg`, `comm`, `S1`~`S5`, `score`, `rock` 임. 피폭 속성은 격자에 없고 데모가 실행 중에 계산함.
- 레이어별 루브릭은 `data/layers.json` 에 있음.

---

## 5. 안전 게이트: 보조 도구, 안전 우선

생명점수는 과학적으로 가치가 높은 곳만 나타냄. 안전 여부는 별개의 판단이고 둘을 섞지 않음.

```
recommend(cell) =
    0 (잠금)                          if gate_hard(cell) 실패
    science_score × soft_penalty      otherwise

gate_hard = (복귀선 반경 안) AND (경사 ≤ 25°) AND (피폭예산 내)
```

- HARD 게이트는 하드 제약(잠금)임. 복귀선 밖, 급경사, 피폭 초과 칸은 생명점수가 100 이어도 추천하지 않음. 회색으로 표시하고 사유를 보여 주며 go 버튼을 비활성화함.
- SOFT 게이트는 감점이나 가중임. 경사와 토질은 체력 소모를 늘리고(Pandolf η=2.0), 통신 음영은 보수적으로 감점함.
- 복귀선이 가장 우선함. 소모품이 줄면 반경이 줄어, 앞서 추천되던 먼 고득점 지점이 잠김. 산소가 90% 여도 너무 멀면 잠기고, 20% 여도 가까우면 통과함.
- 데모 구현 범위: 경사 25° 초과 칸의 A* 통행 차단과 산소 기준 복귀선이 구현돼 있음. 피폭 예산 게이트와 soft_penalty 곱은 설계 단계임.

### 구조의 근거 (NASA 문헌)

NASA 가 개발 중인 PersEIDS(Personalized EVA Informatics and Decision Support)와 같은 방향의 구조임.

- PersEIDS 는 EVA 타임라인에 소모품 사용을 자동 투영하고, 실시간 확률적 안전 평가를 제공하며, 경로를 추천하는 의사결정 보조 시스템임. (NTRS 20230007488)
- 시스템은 추천과 경고(advisory)만 하고 실행 판단은 사람이 함. MARSWALK 도 같음.
- EVA 의사결정 지원 연구의 공통 결론: 도구가 계산을 맡아 운영자가 상위 판단에 집중하게 하고, 안전과 시간의 트레이드오프를 여러 경로에 대해 동시에 평가해 제시함. (SpaceCHI 2025, 10.4230/OASIcs.SpaceCHI.2025.25, Miller & Feigh, Georgia Tech)

### 권한 원칙 (앱에 적용할 규칙)

1. 앱은 보조 도구임. 추천, 경고, 점수만 제공하고 명령하지 않음.
2. 최종 go/no-go 는 우주인이 판단함. 모든 추천은 우주인이 수용하거나 기각할 수 있음.
3. 안전 게이트는 끌 수 없음. HARD 게이트 해제는 우주인의 명시적 수동 확인을 거쳐야 하고 자동으로 무시할 수 없음. 안전이 과학보다 항상 우선함.

---

## 6. 구현 체크리스트

- [ ] `data/weights.json` 을 읽어 지표, 순위, ROC/RS 를 로드. UI 는 순위 드래그로 재배열(숫자 직접 입력 아님).
- [x] 각 칸 Sᵢ 채점 → 생명점수 히트맵: S1, S2 실데이터로 구현(`scripts/build_grid.py`), 전 칸 score 채움.
- [ ] 안전 레이어는 점수에 합산하지 않음. 게이트로만 사용.
- [ ] 잠긴 칸: 회색 + 사유("복귀선 밖" 등) + go 비활성.
- [ ] 복귀선 반경은 소모품 모델(`docs/1_model_spec_handoff.md` §3, §10)과 실시간 연동.
- [x] `grid.geojson`, `grid.js` 전처리: DEM 경사 + CRISM(S1) + SIM 3464(S2) + THEMIS(rock). 완료. 남은 것은 S5 레이어 투입임(S4 물 활동, S3 염류는 설계 완료 미적용).

---

## 7. 근거 출처 (이 문서)

- iMOST: Des Marais et al. (2018) "Seeking the Signs of Life", NTRS 20180003291. https://ntrs.nasa.gov/api/citations/20180003291/downloads/20180003291.pdf
- Hartz & George (2022) "Quantitative Framework for Astrobiology Strategies and in situ Biogenic Assessments" *Front. Astron. Space Sci.* 9:769607. https://doi.org/10.3389/fspas.2022.769607
- ExoMars Biosignature Score: Torres, Sefton-Nash, Vago (2022) EPSC2022-912. https://doi.org/10.5194/epsc2022-912
- CoLD scale: Green et al. (2021) "Call for a framework for reporting evidence for life beyond Earth" *Nature* 598:575-579. https://doi.org/10.1038/s41586-021-03804-9
- 점토 보존: McMahon et al. (2018), Hickman-Lewis et al. (2025) *Nat. Commun.* 10.1038/s41467-025-57727-4, Broz (2020) *Life* 10.3390/life10070113
- S1 CRISM 광물맵: Parente, Itoh, Saranathan "Jezero crater mineral map", Zenodo 5575824. https://doi.org/10.5281/zenodo.5575824 (Icarus 2021 방법 논문: Itoh & Parente, Saranathan & Parente)
- S2 지질맵: Sun, V. Z. & Stack, K. M. (2020) "Geologic map of Jezero crater and the Nili Planum region, Mars", USGS SIM 3464. https://doi.org/10.3133/sim3464
- ROC/RS 가중치: Barron & Barrett (1996) *Management Science* 42(11):1515-1523, Barron (1992), Stillwell et al. (1981)
- 의사결정 보조 (PersEIDS): NASA NTRS 20230007488, Miller & Feigh (GT), SpaceCHI 2025 (10.4230/OASIcs.SpaceCHI.2025.25)


---

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


---

# MARSWALK 검증 현황 (Verification Status) (2026-11-15)

> 생명점수 격자(`grid.js`, `grid.geojson`) 파이프라인에서 어떤 항목이 실데이터로 채워졌는지 정리한 문서임.
> 등급: 실측(실데이터, 실측), 논문(논문 공식이나 값), 추정(근거 있는 추정), 비데이터(미투입 또는 데이터가 아닌 것)

---

## 0. 요약

생명점수는 S1(CRISM 광물)과 S2(SIM 3464 지질) 실데이터로 전 칸(100%)을 채움. 미투입으로 남은 과학 지표는 S5(로버 근접) 하나임. S4(물 활동)와 S3(염류)는 설계 완료, 미적용임. S4 는 S1, S2 에 이미 반영돼 있고 S3 는 Jezero 에 염류가 드묾. 안전(경사, 교신)은 DEM 실데이터로 반영돼 있음.

---

## 1. 생명점수 지표 투입 현황

| 지표 | 입력 | 출처 | 상태 | 커버리지 |
|---|---|---|---|---|
| S1 함수/점토광물 | CRISM 광물 분류맵 | Zenodo 5575824 (Parente, Itoh, Saranathan) | 실측. 격자화 완료 | 2,488 / 3,067칸 (81.1%) |
| S2 퇴적, 델타 맥락 | USGS 지질맵 SIM 3464 | Sun & Stack 2020, doi:10.3133/sim3464 | 실측. 격자화 완료 | 3,067 / 3,067칸 (100%) |
| S3 보존성 염류 | Jezero 에 드묾 | 없음 | 논문. 설계 완료, 미적용 | 해당 적음 |
| S4 물 활동 | S1, S2 에 내재 | 없음 | 논문. 설계 완료, 미적용 | 이미 반영 |
| S5 로버 현장 근접 | (Perseverance, MSL) | 없음 | 비데이터. 미투입 | 없음 |

> 번호 규약: 코드와 가중치 기준으로 S4 가 물 활동(순위 3, ROC 0.157), S3 가 염류(순위 4, ROC 0.090)임.

미투입은 S5 하나이고 S3, S4 는 설계 완료, 미적용임.

- S4 물 활동: S1(점토, 함수광물)과 S2(델타, 퇴적)가 모두 물로 형성, 퇴적된 지표라 과거 물 활동은 이미 반영돼 있음. 따로 투입하면 같은 물 신호를 두 번 세게 되므로 루브릭과 가중치(순위 3, ROC 0.157)는 설계로 유지하고 투입하지 않음.
- S3 보존성 염류: Jezero 는 염류가 드물어(주 신호가 점토, 탄산염, 델타) 변별력이 낮음. 설계는 유지하고 투입하지 않음.

---

## 2. 생명점수(score) 산출 현황

- 방식: 투입된 지표만 재정규화함. `score = Σ(wᵢ·Sᵢ, 투입된 i) / Σ(wᵢ, 투입된 i) / 4 × 100`. 없는 값은 채우지 않음.
- 가중치(ROC): S1 0.457, S2 0.257, S4 0.157, S3 0.09, S5 0.04. 현재 분모는 0.457 + 0.257 = 0.714.
- 커버리지: score 가 채워진 칸 3,067 / 3,067 (100%). S2 가 전 영역을 덮어 전 칸이 산출됨.
- 분포: 최소 / 평균 / 최대 = 25 / 42.7 / 100. 10점 구간별로 20점대 1,924칸, 30점대 27, 40점대 9, 50점대 341, 60점대 36, 70점대 329, 80점대 279, 90점대 23, 100점 99.

| 지표 | 채워진 칸 | 최소 / 평균 / 최대 |
|---|---|---|
| S1 | 2,488 (81.1%) | 1 / 2.04 / 4. 값 분포 1점 1,396, 3점 690, 4점 402 |
| S2 | 3,067 (100%) | 0.2 / 1.44 / 4.0 (반올림 기준 0점 9, 1점 2,526, 2점 74, 3점 70, 4점 388) |
| score | 3,067 (100%) | 25 / 42.7 / 100 |

---

## 3. 핀 4개의 생명점수 (격자에서 읽음)

데모 핀의 점수는 고정값이 아니라 그 위치의 격자 score 를 읽은 값임. 반경 800m 안에 점수 칸이 있으면 그 값을 쓰고, 없으면 추정값으로 대체함.

| 핀 | score | 구성 | 출처 |
|---|---|---|---|
| 델타 전선 | 84 | S1=3 (점토 혼합) + S2=4 (델타 팬) | 격자 |
| Cheyava 방향 | 25 | S1=1 + S2=1 (호저) | 격자 |
| Hawksbill Gap | 25 | S1=1 + S2=1 | 격자 |
| Séítah | 29.5 (표시 30) | S1=1 + S2=1.5 | 격자 |

델타 전선만 84점이고 나머지는 25~30점임. 호저를 화성암으로 반영한 결과임.

---

## 4. Jezero floor 의 S2 를 1 로 낮춤 (Perseverance 실측 반영)

- SIM 3464 매핑 당시 "Jezero floor unit" 은 퇴적암과 화성암이 섞인 것으로 해석돼 초기에는 S2=2 로 둠.
- Perseverance 착륙 후 바닥이 화성암(Máaz 분출암, Séítah 올리빈-휘석 화성암질)으로 확인됨. 퇴적이 아니므로 S2 를 2 에서 1 로 낮춤(`scripts/make_s2.py` 의 `NAME2S2`).
- 영향: 호저 칸 다수가 25점으로 내려가 score 평균이 51.3 에서 42.7 로 바뀜(51.3 은 기록값). 델타 팬(S2=4)은 그대로라 화성암 바닥과 델타 퇴적지의 점수 차이가 커짐.

---

## 5. 안전 레이어 (점수가 아니라 게이트)

| 항목 | 입력 | 상태 |
|---|---|---|
| 경사 `slope_deg` | Jezero CTX DEM 20m (USGS) | 실측 (전 칸). 0.5 / 3.1 / 22.7° |
| 교신 `comm` clear/shadow | 같은 DEM 시선 판정, 안테나 15m | 실측 (전 칸). clear 2,483칸, shadow 584칸 |
| 암석 피복 `rock` | THEMIS 열관성 (Zenodo 4931348, Edwards & Buz 2021) | 실측. 격자화 (rock 0~1, 이 격자에서는 0~0.32). 경로 비용 가중에 씀 |

> 경로 탐색 A\*: 경사와 암석 비용함수로 급경사를 피함. 델타 전선까지 직선 22.7°, 우회 11.2° 는 기록값임.

---

## 6. 재현 방법

저장소 루트에서 실행함.

```
# S2 래스터 생성 (SIM 3464 지질 폴리곤 → S2 0~4)
python scripts/make_s2.py          # → data/s2_jezero.tif

# 생명점수 격자 생성 (S1 CRISM + S2 지질 + DEM 경사/교신 + rock 열관성)
python scripts/build_grid.py --dem jezero_dem.tif \
  --crism zenodo_5575824/jezeroFinal.tif \
  --geo data/s2_jezero.tif --geo-scored \
  --rock zenodo_4931348/Jezero_Thermal_Inertia_v1.tiff \
  --out grid.js --clip-km 5 --cell-px 8 --antenna-h 15
```

산출 `grid.js`: 칸 약 160m, 기지 5km 클립, 3,067칸. `_meta.score_note` 는 "score=가용지표 재정규화, 현재 S1(CRISM 점토·탄산염)+S2(SIM3464 퇴적·델타) 기반" 임. `--rock` 을 빼면 `rock` 이 전 칸 null 로 나옴.

---

## 7. 남은 작업

- [x] S4 물 활동, S3 염류는 설계 완료, 미적용으로 정리함. S4 는 S1, S2(점토, 델타, 둘 다 물 지표)에 이미 반영돼 있고 S3 는 Jezero 에 염류가 드묾. 루브릭과 가중치는 설계로 남김.
- [ ] S5 로버 근접(Perseverance 트래버스) 레이어 투입. 투입하면 score 가 다시 혼합됨.
- [x] `data/weights.json` 이 저장소에 있고 `build_grid.py` 가 기본으로 읽음(`--weights`). 파일을 읽지 못할 때만 내장 ROC 기본값을 씀. 두 값은 같음.
- [ ] S1 커버리지(81.1%)의 미식별(검정) 칸. 필요하면 보간이나 인접 투표로 채우는 방안을 검토함.

---

## 8. 출처

- S1: Parente, Itoh, Saranathan, "Jezero crater mineral map", Zenodo 5575824. https://doi.org/10.5281/zenodo.5575824
- S2: Sun, V. Z. & Stack, K. M. (2020), "Geologic map of Jezero crater and the Nili Planum region, Mars", USGS SIM 3464. https://doi.org/10.3133/sim3464
- 보존 근거: Broz (2020) *Life* 10.3390/life10070113, iMOST (Des Marais 2018)
- floor 화성암: Mars 2020 / Perseverance 착륙지 분석 (Máaz, Séítah 화성암질)
- 암석 피복: Edwards & Buz (2021) THEMIS Jezero TI, Zenodo 4931348. https://doi.org/10.5281/zenodo.4931348


---

# MARSWALK 남은 작업

> 2026-11-14 작성, 2026-11-15 격자 산출 이후 상태로 갱신함. 저장소에는 데이터, 모델 문서, 지도 데모가 들어 있고 아래는 그 다음 단계의 작업임.

## 1. 앱 구현 (개발 전환 시 필수)

1. 앱 실제 구현: React + Leaflet + Recharts + Zustand.
   - 모델(대사율, 산소, 복귀선, 체력, 심박, 피폭, 생명점수)을 순수 함수로 이식함. 참조: `marswalk_grid_demo.html`, `docs/1_model_spec_handoff.md`, `docs/12_api_data_spec.md`.
   - 패드(계획)와 HUD(현장) 양면 UI.
2. `grid.geojson` 앱 연동: Leaflet GeoJSON 레이어로 경사, 교신을 색칠함.
   - 안전 게이트 적용: `slope_deg>25` 또는 복귀선 밖이면 잠금(회색), `comm=shadow` 이면 교신 경고(참고용).
   - 연동 예시: `docs/8_grid_guide.md` §5.

## 2. 데이터 보강 (선택)

3. 생명점수 지표 채우기.
   - 완료: S1(CRISM 광물맵), S2(USGS SIM 3464) 를 격자에 투입함. CRISM 은 범례 색 룩업, S2 는 사전 점수 래스터의 칸 평균으로 채점함. 1밴드 연속형 래스터를 넣을 때 쓰는 5~95 퍼센타일 정규화는 예시 수준이라 실제 단위에 맞춘 루브릭 고정이 필요함.
   - 남음: S5(로버 근접, Perseverance 트래버스) 레이어 투입. 투입하면 score 가 다시 혼합됨.
   - 남음: S1 미식별 칸 579개(커버리지 81.1%) 처리 방침. 현재는 보간하지 않고 비워 둠.
   - 재생성 명령: `python scripts/build_grid.py --dem jezero_dem.tif --crism zenodo_5575824/jezeroFinal.tif --geo data/s2_jezero.tif --geo-scored --rock zenodo_4931348/Jezero_Thermal_Inertia_v1.tiff --out grid.js --clip-km 5 --cell-px 8 --antenna-h 15`
4. 장비 무게.
   - 완료: 공구, 시료통, PLSS 질량을 아폴로 문서값으로 채움(`data/equipment.json`, Allton 1989 JSC-23454, NASA ALSJ).
   - 남음: 수트 질량(아폴로 A7L, NASA xEMU)은 수록하지 않음.
5. 방사선 장소 보정식: 현재는 근사식임(방향은 RAD 실측과 일치). 필요하면 천정각 의존(초기 메모에는 Guo 2023 으로 적혀 있음. `docs/2_sources.md` §8 의 해당 문헌은 Khaksarighiri 2023)으로 정교화함. 고도 보정 `altF` 는 설계 문서에만 있고 데모에는 없음.
6. 다중 소모품 복귀 한계: 설계와 용량 데이터(`data/consumables.json`)까지만 있고 데모에는 산소 기준 복귀선만 구현됨.

## 3. 하지 않는 것

- 생명점수 가중치의 데이터화: 가중치는 측정할 수 있는 양이 아니라 지표의 중요도임. 순위를 문헌으로 정하고 ROC 공식으로 계산하는 현재 방식을 유지함.
- 교신 음영 정밀화(전파 세기, 중계 위성): 참고용 레이어라 필수가 아님. 초기 문서에는 EVA 범위에서 영향이 2% 수준이라는 기록이 있으나 계산 근거가 저장소에 없어 다시 확인하지 못함.


---

# MARSWALK HUD 데이터 매핑 명세 (2026-11-15)

> HUD 는 새 데이터를 쓰지 않음. 패드(PAD)와 같은 격자, 모델, 정적 데이터를 읽어 현장용 최소 화면으로 표시함.
> HUD 요소별로 읽는 데이터와 모델을 고정해 둔 문서임. 데이터 작업은 없고 전부 프론트(UI) 작업임. 이 저장소에는 HUD 구현이 없고 매핑 명세만 있음.

---

## 0. 원칙

- HUD 는 PAD 데이터를 재사용함. 같은 Zustand store 를 구독하고 최소 필드만 렌더함.
- 표시 기준: 지금 보지 않으면 생명이 위험한 정보만 HUD 에 둠. 나머지는 PAD 에 둠.
- UI 만 다름(큰 글씨, 고대비, 물리 버튼). 데이터와 모델은 같음.

---

## 1. HUD 페이지별 데이터 매핑

| HUD 요소 | 읽는 데이터, 모델 | 출처 | PAD 와의 관계 |
|---|---|---|---|
| H1 복귀 여유 | walk-back 반경 − 현재 거리 | 소모품, 복귀선 모델 | 동일 |
| H1 산소 | o2 잔량 | 산소 모델 (아폴로 PLSS) | 동일 |
| H1 방위와 거리 | 현위치 → 목적지 벡터 | 위치 + 지도 (기하) | 동일 |
| H1 회피 큐 | grid `slope_deg>25`, `comm=shadow` | DEM 격자 | 동일 |
| H1 버디 간격 | 두 번째 대원 위치 − 내 위치 | 위치 입력 (신규) | 신규 (데이터셋 아님) |
| H2 작업 항목 | 미션 작업 리스트 | 입력 | 해당 없음 |
| H2 잔여 체류 시간 | walk-back 여유 / 소모율 | 복귀선, 소모품 | 동일 |
| H2 지점 영상 대조 | Perseverance 실사 | spots (raw API) | 동일 |
| H3 영상 마킹 | 카메라 프레임 + 위치 태그 | 기기 (카메라, 신규) | 기능 (데이터 아님) |
| H3 음성 받아쓰기 | 마이크 → STT | 기기 (마이크, 신규) | 기능 |
| H3 메타데이터 자동 첨부 | 위치, 시각, 대원 상태 | 기존 store | 동일 |
| H4 경보 내용 | 안전 게이트 트리거 (복귀선, 피폭, 산소) | 모델 로직 | 동일 |
| H4 물리 버튼 매핑 | 선택지 → 하드웨어 키 | 기기 (버튼, 신규) | UX |
| H4 합의 분기 | 대원과 관제의 확인 플로우 | 로직 | 해당 없음 |
| H5 복귀 개시 안내 | point of no return 판정 | walk-back 모델 | 동일 |
| H5 기지 방위 | 현위치 → 기지 벡터 | 위치 + 기지 (기하) | 동일 |
| H5 남은 거리 | 기지까지 거리 | 기하 | 동일 |

17개 요소 중 11개가 PAD 와 같은 데이터를 읽음. HUD 고유 추가분은 데이터셋이 아니라 위치 입력, 기기 기능, UX 임.

---

## 2. HUD 고유 항목 (데이터 아님)

| 항목 | 성격 | 필요한 것 |
|---|---|---|
| 버디 위치 | 위치 입력 | 두 번째 대원 좌표 피드 (실제 임무에서는 수트 텔레메트리) |
| 영상 마킹, 음성 STT | 기기 기능 | 카메라, 마이크 API |
| 물리 버튼 | 하드웨어 UX | 수트 입력 매핑 |

세 항목 모두 과학 데이터셋이 아니라 기기와 입력 연동임. 데이터 작업 범위가 아니고 개발, 하드웨어 범위임.

---

## 3. 개발 메모

- HUD 화면은 PAD 와 같은 store 를 구독하고 최소 필드만 큰 글씨, 고대비로 표시함.
- 회피 큐와 경보는 PAD 의 안전 게이트 로직을 그대로 재사용함. 중복 구현하지 않음.
- H3 기록은 기기 API(카메라, 마이크)와 연동하고, 위치, 시각, 상태는 store 에서 자동 첨부함.
- 물리 버튼은 선택지를 키 이벤트에 매핑함.

---

## 4. 데이터 관점 정리

- HUD 용 새 데이터나 전처리는 없음. 같은 데이터 파일 묶음으로 PAD 와 HUD 를 모두 처리함.
- HUD 는 프론트(UI) 작업과 기기 연동(카메라, 마이크, 버튼)으로 구성됨.
- 데이터 쪽에서 넘기는 것은 이 매핑 문서와 기존 데이터(격자, 모델, 정적 파일)임.


---

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
