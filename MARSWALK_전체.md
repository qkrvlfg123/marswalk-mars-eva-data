# MARSWALK — 데이터 검증 현황 (업데이트 2026-11-15)

> 기능별 "어느 데이터 → 받을 수 있나 → 검증 → 투입값 → 등급" 한눈 정리. 발표 Q&A·운영진 설명 방어용.
> 등급: 🟩 실측/실데이터 · 🟦 논문 공식·값 · 🟨 근거 있는 추정(교체 가능) · ⬜ 데이터 아님(공식·기하·설계)
> 상세: `README.md` · `docs/7_biosignature_design.md` · `docs/9_verification_status.md`

---

## ★ 생명점수 검증 현황 (2026-11-15) — S1·S2 실데이터, 커버리지 100%

| 지표 | 입력(실데이터) | 출처 | 상태 | 커버리지 |
|---|---|---|---|---|
| **S1** 함수/점토광물 | CRISM 광물 분류맵 | Zenodo 5575824 (Parente·Itoh·Saranathan) | 🟩 실데이터 | 2,488/3,067 칸 (81.1%) |
| **S2** 퇴적·델타 맥락 | USGS 지질맵 SIM3464 | Sun & Stack 2020 (doi:10.3133/sim3464) | 🟩 실데이터 | 3,067/3,067 칸 (100%) |
| **S4** 물 활동 · **S3** 염류 | S1·S2에 내재 / Jezero 희박 | — | 🟦 **설계완료·비적용** | — |
| **S5** 로버 근접 | — | — | ⬜ **미투입(유일)** | — |

- **생명점수(score) = S1+S2 실데이터, 전 칸(100%) 채움.** min/평균/max = **25 / 42.7 / 100**. 산출 `grid.js`(칸≈160m, 기지 5km 클립, 3,067칸).
- **방식 = 가용 지표만 재정규화:** `score = Σ(wᵢ·Sᵢ, 투입된 i) / Σ(wᵢ, 투입된 i) / 4 × 100` (가짜값 안 채움, 현재 분모 = w_S1+w_S2 = .714). S3~S5 투입 시 자동 재혼합.
- **Jezero floor unit = S2 1** — Perseverance 착륙 후 바닥이 **화성암(Máaz/Séítah 화성암질)** 확인 → '퇴적'에서 하향. 델타 팬(Jezero fan) = S2 4.
- **핀 4개(격자 실데이터):** 델타 전선 **84**(S1=3+S2=4) · Cheyava 25 · Hawksbill 25 · Séítah ~30.
- **S4 물 활동·S3 염류 = 설계완료·비적용:** S4(물 활동)는 S1(점토)·S2(델타)가 둘 다 물 형성·퇴적 지표라 이미 반영(이중계산 방지), S3(염류)는 Jezero 염류 희박. 둘 다 ROC 가중치는 설계로 유지, 미투입. → 실제 미투입은 **S5(로버 근접) 하나.** 경사·교신은 DEM 실데이터로 이미 전 칸 반영.

---

## A. 실데이터 / 실측 검증 🟩

| 기능 | 데이터셋 | 받기 | 투입값 | 검증 |
|---|---|---|---|---|
| **심박** | PhysioNet 트레드밀 992명 | ✅ raw 받아 보정 (`calibrate_hr.py`) | HR = 70.5 + 113.2·%VO2 | R²=0.77, n=56만 |
| **방사선** | Curiosity RAD (Hassler 2014) + 지형차폐 (Guo 2026) | ✅ NASA PDS raw | 0.64 mSv/day · 차폐 ~20% | 화성 표면 직접측정 |
| **지형 경사** | Jezero CTX DEM 20m (USGS) | ✅ 격자화 (`build_grid.py`) | 0.5 / 3.1 / 22.7° (5km 클립) | Jezero 지형 부합 |
| **교신 음영** | 같은 CTX DEM (가시선) | ✅ 격자화 (안테나 15m) | clear 2,483 / shadow 584칸 | 근거리 비이슈 |
| **생명점수 S1** | CRISM 함수광물(점토·탄산염) | ✅ 격자화 | S1 0~4, 커버리지 81% | 점토·탄산염=생명 유력 지표 |
| **생명점수 S2** | USGS SIM3464 지질(퇴적·델타) | ✅ 격자화 | S2 0~4, 델타 전선 최고점(84) | Jezero 바닥=화성암→S2=1 (Perseverance 지상검증) |
| **암석도** | THEMIS 열관성 (Zenodo 4931348, Edwards&Buz 2021) | ✅ 격자화 | rock 0~1, 바닥 0~0.32 | 저열관성=모래 |
| **경로탐색** | A*(경사·암석 비용) | ✅ 검증 | 델타 전선 22.7°→11.2° | 급경사 회피 확인 |
| **POV 실사** | Mars2020 raw image API | ✅ 받음 (`fetch_pov.py`) | 델타 sol 400대 | Perseverance 실촬영 |
| **지도 타일** | OpenPlanetary / Mars Trek | ✅ | MOLA·THEMIS·HiRISE·CRISM | — |
| **우주기상** | NASA DONKI API | ✅ 받음 | SPE/CME 이벤트 | — |

## B. 논문 공식 / 값 🟦

| 기능 | 출처 | 투입값 |
|---|---|---|
| **대사율** | Pandolf 1977 (NASA JSC EVA traverse) | M_W 식 |
| **생리 기준** | ISS 승무원 (NTRS 20220014309) | VO₂peak 37.5/42.1 · 지속가능 35% |
| **지형계수 η** | 레골리스≈느슨한 모래 (Soule&Goldman) | η = 2.0 |
| **소모품 (PLSS)** | 아폴로 15-17 실측 (NTRS) | 산소·냉각수 5.2L·CO₂ 3.12lb·배터리 390Wh |
| **피로/체력** | W'BAL (Coats 2003) | 지속가능 초과→소모, 이하→회복 |

## C. 격자 전처리 — 실행·검증 완료 ⭐ (S1·S2 실데이터 반영)

- **입력:** Jezero CTX DEM 20m/px (USGS, 90MB) + CRISM 광물맵(Zenodo 5575824) + USGS 지질맵 SIM3464.
- **스크립트:** `make_s2.py`(지질 폴리곤→S2 래스터) → `build_grid.py`(DEM 경사·교신 + S1 + S2 → 격자).
- **산출:** `make_s2.py` → `data/s2_jezero.tif` → `grid.js` — **3,067칸**(칸≈160m, 기지 5km 클립). `window.GRID` 전역.
- **결과:** 경사 0.5/3.1/22.7° · 교신 clear 2,483/shadow 584 · **S1 2,488칸(81.1%) · S2 3,067칸(100%) · score 3,067칸(100%, 25/42.7/100)**.
- **의미:** **S1(CRISM)·S2(SIM3464)·암석도(THEMIS)·A\* 전부 채움·검증 완료.** 경사·교신·생명점수 전부 실데이터. S4 물활동·S3 염류는 설계완료·비적용 → 남은 건 S5(로버 근접) 투입뿐.
- **메모:** Jezero 바닥은 Perseverance 지상검증 결과 화성암(Máaz/Séítah)이라 S2 2→1 하향, 델타 팬만 고점.
- **생성:** `python build_grid.py --dem jezero_dem.tif --crism zenodo_5575824/jezeroFinal.tif --geo data/s2_jezero.tif --geo-scored --out grid.js --clip-km 5 --cell-px 8 --antenna-h 15`

## D. 데이터가 아닌 것 — 공식·기하·설계 ⬜

| 항목 | 성격 | 근거 |
|---|---|---|
| **생명점수 가중치** | 데이터셋 **불가능**(중요도) | 순위=iMOST·Hartz&George / 숫자=Barron ROC (0.457·0.257·0.157·0.090·0.040) |
| **복귀선 ÷2** | 정확한 **기하** | 갈=올 → 반, 예비분 15% |
| **안전 게이트·25° 컷** | **설계 선택** | 임계값은 로버 등반한계 문헌으로 받칠 수 있음 |
| **장비 무게** | 대표값 🟨 | 우주복·PLSS 질량 문서화됨 → 올릴 수 있음 |

→ 진짜 "데이터 자체가 존재 불가"는 **생명점수 가중치 하나뿐.**

---

## 한 줄 방어
> *"대사율·생리값은 NASA/ISS 논문, 심박은 PhysioNet 992명 실측 검증(R²=0.77), 방사선은 Curiosity RAD 직접측정, 소모품은 아폴로 실측, 경사·교신은 실제 Jezero CTX DEM 20m 격자화. **생명점수도 S1=CRISM 광물맵·S2=USGS 지질맵(SIM3464) 실데이터로 전 칸(100%) 채웠고**, Jezero 바닥은 Perseverance 실측 반영해 퇴적 점수를 낮췄습니다. 가중치만 측정 불가능한 '중요도'라 과학 순위 + Barron ROC 공식으로. 전부 출처·등급 공개."*


---

# MARSWALK — 추후 할 일 (TODO)

> 2026-11-15 기준. 지금 핸드오프 키트로 발표는 방어 가능. 아래는 "더 조이거나 실제 개발" 단계.

## 🔴 필수 (개발 전환 시)
1. **앱 실제 구현** — React + Leaflet + Recharts + Zustand.
   - 모델(대사율·산소·복귀선·체력·심박·피폭·생명점수)은 **순수 함수**로 이식. 참조: `marswalk_demo.html`, `1_model_spec_handoff.md`.
   - 패드(계획) / HUD(현장) 양면 UI.
2. **grid.geojson 앱 연동** — Leaflet GeoJSON 레이어로 경사·교신 색칠.
   - 안전 게이트 적용: `slope_deg>25` 또는 복귀선 밖 → 잠금(회색), `comm=shadow` → 교신 경고(참고용).
   - 연동 예시: `8_grid_guide.md` §5.

## 🟡 데이터 더 조이기 (선택, 신뢰도↑)
3. **생명점수 칸 Sᵢ 채우기 — S1(CRISM)·S2(SIM3464)·암석도(THEMIS)·A\* 전부 채움·검증 완료.**
   `python build_grid.py --dem jezero_dem.tif --crism zenodo_5575824/jezeroFinal.tif --geo data/s2_jezero.tif --geo-scored --out grid.js --clip-km 5 --cell-px 8 --antenna-h 15`
   - S1 루브릭 = **범례 RGB 최근접 분류 → 칸 footprint 최빈 광물**(퍼센타일 아님). S2 = 지질유닛별 점수 footprint 평균.
   - **S4(물 활동)·S3(염류) = 설계완료·비적용** (S4는 S1·S2에 반영, S3은 Jezero 희박). **남은 것: S5(로버 근접) 투입** → score 자동 재혼합.
4. **장비 무게 🟨 → 논문값** — 아폴로 A7L+PLSS / NASA xEMU 질량으로 교체(대표값 탈피).
5. **방사선 장소보정 식** — 현재 근사(방향은 RAD 실측). 필요시 Guo 2023 천정각 의존으로 정교화.

## 🟢 발표 준비
6. **데모 영상** — `marswalk_demo.html` 시나리오(핀 선택→생명점수→복귀선 수축→귀환) 30초~1분 녹화.
7. **스토리 3축** — ① 왜 사람(로봇 한계) ② 안전 최우선·보조도구(PersEIDS식) ③ 데이터 검증(이 키트).
8. **검증현황 1장**(`9_verification_status.md`)으로 Q&A 방어.

## 참고 — 안 해도 되는 것 (정직성)
- **생명점수 가중치**: 데이터 못 구함이 아니라 측정 불가능한 '중요도'. ROC 공식이 답. 더 할 것 없음.
- **교신 음영 정밀화**(전파세기·중계위성): 참고용 레이어라 필수 아님. EVA 범위 2%로 비이슈 확인됨.


---

# MARSWALK 모델 스펙 — 개발 핸드오프 (2026-11-14)

> 개발팀용. **각 계산이 뭔지 + 공식 + 입출력 + 상수(출처).** 참조 구현: `marswalk_demo.html` (이 로직의 동작 레퍼런스).
> 상수 출처 상세는 `모델근거_출처` 문서 참고. UI는 자유 (React 등). **이 로직만 그대로 옮기면 됨.**

---

## 0. 이게 뭔지 (한눈에)

화성 기지 대원 EVA 도보 내비. 핵심 계산 6개:
1. **대사율** (경사·무게 → 에너지) → 2. **산소 소모/잔량** → 3. **복귀 반경(walk-back)** → 4. **체력** → 5. **피폭** → 6. **생명점수(지점 선택)**

전부 순수 함수 (입력 → 숫자 출력). UI·지도와 독립.

---

## 1. 대사율 (Pandolf 방정식)
**뭔지:** 대원이 얼마나 힘든지 = 분당 에너지. 모든 소모의 출발점.

```
G    = tan(경사도°) × 100                       # grade (%)
M_W  = 1.5·M + 2.0·(M+L)·(L/M)² + η·(M+L)·(1.5·v² + 0.35·v·G·g_mars)
```
- 입력: `M`=체중kg, `L`=하중kg, `v`=속도 m/s, 경사도°
- 출력: `M_W` = 대사율 (watts)
- 상수: `η=2.0`(화성 레골리스≈모래), `g_mars=0.38`(복귀=내리막은 G=0 보수)
- 출처: NASA JSC EVA traverse 모델 (Pandolf 1977)

## 2. 산소 소모 · 잔량
**뭔지:** 대사율 → 산소 소모율 → 산소통이 줄어듦.

```
O2_rate = M_W / 348                 # L/min  (산소 1L ≈ 20.9 kJ)
대사율_kcal_hr = M_W × 0.86
o2(t+Δ) = o2(t) − O2_rate · Δt      # 잔량, TANK=500 L (≈8h)
```
- 출력: `O2_rate`(L/min), `o2`(잔량 L)

## 3. 복귀 반경 (walk-back) ★ 핵심 — 편도 아님, 왕복!
**뭔지:** "지금 소모품으로 **갔다가 돌아올 수 있는** 최대 거리." 안전의 핵심 지표.

```
남은거리  = (o2 / TANK) × MAXWB          # 남은 총 보행거리(m). MAXWB=2000(만땅)
반경     = (남은거리 − MAXWB·RESERVE) / 2   # ★ ÷2 = 편도 아님(갈+올), RESERVE=0.15 예비분
복귀판정: 기지까지_거리 ≥ 반경  →  🔴 복귀선 도달·귀환
          > 반경×0.8          →  🟡 근접
          그 외               →  🟢 여유
```
- **왜 ÷2:** 반경만큼 나가면 그만큼 되돌아와야 함. 편도로 쓰면 못 돌아옴(고립). 그래서 나갈 수 있는 거리는 남은거리의 절반.
- **예비분(RESERVE 15%):** 역풍·오르막·실수 대비 안전마진. 도착 시 이만큼 남게.
- **point of no return:** 기지거리 = 반경이 되는 순간이 복귀 불능점. 넘기면 귀환 불가 → 자동 귀환 트리거.
- **실시간 드레인:** 경사(오르막/내리막)가 Pandolf로 매 틱 소모율에 반영 → 산소·체력이 실시간으로 닳고 반경도 수축. (전부 §1 대사율·§2 산소에서 나오는 값, 새 데이터 불필요.)
- 소모품 줄면 반경 수축 → 먼 고득점 지점이 자동 잠김. (산소 90%라도 멀면 잠금, 20%라도 가까우면 통과.)
- 지점 잠금(planning): 목적지 D까지 왕복 가능 ⟺ `2·D ≤ 남은거리 − MAXWB·RESERVE`.
- 다중 소모품 확장: 반경을 산소·냉각수·CO2·배터리 각각 계산 후 **MIN**(가장 먼저 바닥나는 것이 결정). → `data/consumables.json`.

## 4. 체력 (W'BAL 개념)
**뭔지:** 지속가능 강도 넘으면 지침, 아래면 회복.

```
%VO2 = O2_rate / VO2abs             # VO2abs = VO2peak·M/1000 = 3.0 L/min
stam(t+Δ) = stam + (%VO2 > 0.35 ? −14·(%VO2−0.35) : +8·(0.35−%VO2)) · Δt
                                     # 0~100 clamp
```
- 상수: `VO2peak=37.5` ml/kg/min(ISS 승무원), 지속가능 `0.35`(30~40%)
- 출처: Coats 2003 / W'BAL (critical power)

## 5. 심박
```
HR = HR_rest + (HRmax − HR_rest)·%VO2  (+이벤트 보정)
```
- 상수: `HR_rest=70`, `HRmax = 220 − 나이(34) = 186`

## 6. 피폭 (방사선)
**뭔지:** 기준선량 × 위치(고도·차폐) × 시간 누적.

```
altF = 1 + 고도_m / 5000            # 높을수록 ↑
shF  = 1 − 0.2 · 차폐율             # 지형 차폐 최대 ~20% (RAD 실측)
dose(t+Δ) = dose + (RAD_DAY/1440)·altF·shF · Δt   # RAD_DAY=0.64 mSv/day
SPE 이벤트 시: dose += 1.2·shF
```
- 출처: Curiosity RAD (Hassler 2014) + 지형차폐 실측 (Guo 2026)

## 7. 생명점수 (지점 선택) — 상세는 `docs/7_생명점수_상세설계.md`
**뭔지:** "어디가 생명 흔적 유력한가" 점수. 지점 정렬·선택용. **보조도구이며 안전 게이트가 우선.**

```
생명점수(cell) = Σ(wᵢ·Sᵢ, 투입된 i) / Σ(wᵢ, 투입된 i) / 4 × 100   # 가용 지표만 재정규화
화면추천(cell) = 안전게이트 × 생명점수                              # 복귀선 밖·급경사·피폭초과 = 잠금
```
- **가용 지표만 재정규화:** 투입된 Sᵢ의 가중치 합으로 나눔(가짜값 안 채움). 지금은 S1·S2만 투입 → 분모 = .457+.257 = **.714**. S3~S5 들어오면 자동 재혼합. 하나도 없으면 null.
- `Sᵢ` = 지점별 증거강도 0~4: **S1 함수/점토광물(CRISM, 실데이터)·S2 퇴적델타(SIM3464, 실데이터)**·S4 물흔적·S3 염류·S5 로버확인.
  - **S1·S2 실데이터 반영 완료**, score 전 칸(100%) 채움(min/평균/max 25/42.7/100). S4 물활동·S3 염류는 설계완료·비적용 → 남은 건 S5.
- `wᵢ` = **지표 순위에서 공식으로 계산** (손으로 안 고름). 순위=iMOST/Hartz&George, 숫자=Barron ROC/RS.
  - ROC 기본(코드 내장): 0.457 / 0.257 / 0.157 / 0.090 / 0.040 (순위 1~5). `data/weights.json` 있으면 그 값 우선.
  - UI는 **순위 재배열**(드래그), 숫자 직접입력 아님.
- **안전 우선:** 생명점수가 100이어도 복귀선 밖이면 추천 안 함(회색+사유). 최종 go/no-go = 우주인.
- 출처: iMOST(Des Marais 2018) · Hartz&George 2022 · Barron&Barrett 1996 · PersEIDS(NTRS 20230007488)

---

## 8. 데이터 입력 포맷

**탐사 지점** (`spots.js` / spots.json):
```js
{ name, lat, lon, score, note, img }   // img = Perseverance 실사 URL
```
**지도:** OpenPlanetary/Mars Trek 타일 URL (Leaflet)
**우주기상:** DONKI API (키 필요) 또는 과거 이벤트 1건 캐시
**격자(경사·점수):** DEM 처리 결과 GeoJSON (추후)

---

## 9. 구현 메모
- 로직 6개는 **순수 함수** → React 훅/유틸로 그대로 이식
- 상태(산소·체력·피폭·위치) → Zustand
- `step()` = 1틱 루프 (데모는 setInterval, 실제는 requestAnimationFrame/타이머)
- 지도 = Leaflet(React-Leaflet), 차트 = Recharts
- 참조 구현 `marswalk_demo.html` 의 `<script>` 에 위 전부 동작 형태로 있음

---

## 10. 다중 소모품 복귀선 (심화, §3 확장)
**뭔지:** 복귀 한계 = 산소 하나가 아니라 **4개 소모품 중 제일 먼저 바닥나는 것.** 참조: `consumables.html`, 데이터 `data/consumables.json`

| 소모품 | 용량(분) | 대사율 비례? |
|---|---|---|
| 산소 | 480 | ✅ |
| 냉각수 | 450 | ✅ (×1.05, 열) |
| CO₂ 스크러버 | 500 | ✅ (×0.95) |
| 배터리 | 420 | ❌ (일정) |

```
M0 = 273 W (기준 대사율 ~930 BTU/hr)
f  = M_W / M0
각 소모: remaining_i -= Δt × (비례? f : 1) × factor_i
복귀까지_분_i = remaining_i / (현재 소모율_i)
복귀 한계 = min(복귀까지_분_i)   ← walk-back 반경을 정함 (산소 아님)
```
핵심: 고강도→냉각수/산소 먼저 · 저강도 장시간→배터리 먼저.
출처: EMU PLSS(NTRS 20140009556) · 아폴로 15-17 8h · 8h@930/5h@1600 BTU/hr

---

## 11. 심박 — 실측 검증값 (§5 업데이트)
`HR = 70.5 + 113.2·%VO2` (PhysioNet 992명 실측 보정, R²=0.77), HRmax 186 캡.
→ 참조 구현 `marswalk_grid_demo.html`도 이 검증값(`HR_A=70.5`, `HR_B=113.2`, HRmax 186 캡)으로 동작함. 스크립트 `scripts/calibrate_hr.py`.


---

# MARSWALK — 생명점수(Biosignature Score) 상세 설계 (업데이트 2026-11-15)

> ① "어디로 갈까"를 정하는 과학 점수. **지표 순위는 프레임워크 근거, 가중치 숫자는 공식 계산, 안전은 별도 게이트가 최우선.**
> 개발 핸드오프용. 로직은 전부 데이터(JSON)로 분리 — `data/weights.json`, `data/layers.json`.
> 전체본: `docs/7_biosignature_design.md`.

---

## ★ 구현 현황 (2026-11-15)

- **S1(CRISM 광물, Zenodo 5575824)·S2(USGS SIM3464, Sun & Stack 2020) 실데이터 반영** → score 전 칸(100%, 3,067칸) 채움. min/평균/max = 25/42.7/100.
- **점수 = 가용 지표만 재정규화**(아래 §1 갱신). 커버리지: S1 81.1% · S2 100% · score 100%.
- **Jezero floor = S2 1**(Perseverance 실측=화성암). 델타 팬 = S2 4.
- **S4 물 활동·S3 염류 = 설계완료·비적용** (S4는 S1·S2에 이미 반영, S3은 Jezero 염류 희박). → 미투입은 **S5(로버 근접) 하나.**

---

## 0. 세 줄 요약

1. **생명점수 = Σ wᵢ·Sᵢ** — 지점마다 지표 5개(Sᵢ, 0~4)를 가중합.
2. **가중치 wᵢ는 손으로 안 고름.** 지표 "순위"만 과학으로 정하면 공식(ROC/RS)이 숫자를 계산. → "왜 0.30이야?" 방어됨.
3. **생명점수는 보조.** 안전(복귀선·경사·피폭)이 별도 게이트로 추천을 잠금. **최종 판단은 우주인, 안전 최우선.**

---

## 1. 점수 공식

```
생명점수(cell) = Σ(wᵢ·Sᵢ, 투입된 i) / Σ(wᵢ, 투입된 i) / 4 × 100   # 가용 지표만 재정규화
# 지표가 하나도 없으면 null (가짜값 안 채움). 현재 투입 = S1·S2 → 분모 = .457+.257 = .714
```

- **Sᵢ = 지점별 증거 강도 (0~4):** 그 셀에서 지표가 얼마나 강하게 나타나나.
- **wᵢ = 지표 중요도 (합=1):** 그 지표가 일반적으로 얼마나 중요한가.
- 역할 분리가 중요: "로버 현장 확인"은 **신뢰도 최고 → 있으면 Sᵢ=4**로 반영하고, 커버리지가 좁으니 **가중치 wᵢ는 낮게**. 모순 없음.

### Sᵢ 0~4 척도 (SSTM·CoLD식 단계)

| 점수 | 뜻 |
|---|---|
| 0 | 신호 없음 |
| 1 | 약한 간접 정황 |
| 2 | 궤도 관측 암시 |
| 3 | 강한 궤도·분광 신호 |
| 4 | 로버 현장 확인 |

근거: MSR SSTM(증거 추적 행렬) · CoLD scale(Confidence of Life Detection, Green et al. 2021 *Nature*)의 "증거 단계" 개념.

---

## 2. 지표 5개 — 순위의 과학 근거

순위 기준 = **iMOST 보존광물 우선순위** + **Hartz & George(2022) 신뢰도/검출도** + **Mars 2020 SDT 생체신호 유형**.

| 순위 | 지표 | 입력 레이어 | 상태 | 근거 |
|---|---|---|---|---|
| 1 | **함수/점토광물** | CRISM 광물맵 (Zenodo 5575824) | ✅ 실데이터 81.1% | iMOST · McMahon 2018 · Hickman-Lewis 2025 |
| 2 | **퇴적·델타 맥락** | 지질 SIM3464 (Sun & Stack 2020) | ✅ 실데이터 100% | Broz 2020 · Gale SAM |
| 3 | **물 활동 흔적** | CRISM 수화 + 수로지형 | ⬜ 미투입 | iMOST 수성맥락 · MSR SSTM |
| 4 | **보존성 염류** | THEMIS/CRISM 염류 | ⬜ 미투입 | iMOST · Osterloo 2008 |
| 5 | **로버 현장 근접** | Perseverance/MSL | ⬜ 미투입 | Mars2020 · CoLD(Green 2021) |

**S1 루브릭(구현):** 범례 RGB 최근접 분류 → 칸 footprint 최빈 광물. 탄산염·점토·함수실리카=4 / 올리빈+점토 혼합=3 / 올리빈·휘석=1 / 미식별·배경=null.
**S2 루브릭(구현):** SIM3464 유닛 폴리곤 래스터화 → footprint 평균. 삼각주 팬(Jezero fan)=4 / 평활 퇴적평원=3 / **Jezero 호저(=화성암 Máaz/Séítah, Perseverance 실측)·etched·풍성사구=1** / 충돌·노출암=0.

전체 링크는 `docs/2_모델근거_출처.md` §8, 상세 설계는 `docs/7_biosignature_design.md`.

---

## 3. 가중치 — 숫자를 안 고르는 법 (핵심)

**문제:** 0.30·0.25·0.20… 을 내가 고르면 "왜 그 숫자?"에 못 버팀.
**해법:** 지표 **순위만** 과학으로 정하고, 순위→숫자는 **공개된 MCDA 공식**으로 계산.

> 출처: **Barron & Barrett (1996)** *Management Science* 42(11):1515-1523. "정확한 가중치를 사람 머리에서 뽑는 건 존재하지 않는 정밀도를 요구한다 → 순위만 받고 surrogate weight로 변환."

### 두 공식

| 공식 | 식 | 특징 |
|---|---|---|
| **ROC** (Rank Order Centroid, Barron 1992) | wᵢ = (1/N)·Σ_{k=i..N}(1/k) | 상위 지표 강하게 강조 |
| **RS** (Rank Sum, Stillwell 1981) | wᵢ = (N+1−i)/Σ | 완만하게 차등 |

### N=5 계산 결과 (합=1.0 검증됨)

| 순위 | ROC | RS |
|---|---|---|
| 1 | **0.457** | 0.333 |
| 2 | 0.257 | 0.267 |
| 3 | 0.157 | 0.200 |
| 4 | 0.090 | 0.133 |
| 5 | 0.040 | 0.067 |

- **기본 = ROC(과학권장).** 상위 지표(점토) 강조가 보존과학과 부합.
- 기존 데모값 0.30/0.25/0.20/0.15/0.10 ≈ **RS와 거의 동일** → RS도 정당한 대안.
- **프리셋 = 순위 바꾸기**(물추적/검증우선). 슬라이더로 숫자를 만지는 게 아니라 **순위를 재배열**하면 공식이 다시 계산.

→ 발표 방어: *"가중치는 제가 고른 숫자가 아니라, 과학 프레임워크로 지표 순위를 정하고 Barron ROC 공식으로 계산한 값입니다."*

---

## 4. 레이어 → 점수 파이프라인

```
[과학 레이어]  CRISM·지질·THEMIS·로버
     │  각 셀에서 레이어값 → Sᵢ(0~4) 루브릭 채점
     ▼
  생명점수 = Σ wᵢ·Sᵢ  →  0~100  →  히트맵
     │
     ▼
[안전 레이어]  복귀선·경사·피폭·통신  →  게이트
     │
     ▼
화면 추천 = 게이트 × 생명점수
```

- 전처리: Jezero DEM·CRISM·지질을 **공통 격자(예 100m)**로 리샘플 → `data/grid.geojson` (셀마다 slope·Sᵢ·rad 속성).
- 레이어별 루브릭은 `data/layers.json`에 수록.

---

## 5. 안전 게이트 — "보조도구·안전 최우선" (설계의 핵심)

**생명점수는 '과학적으로 좋은 곳'만 말한다. 안전하냐는 별개다.** 이 둘을 섞지 않는다.

```
recommend(cell) =
    0 (잠금)                          if gate_hard(cell) 실패
    science_score × soft_penalty      otherwise

gate_hard = (복귀선 반경 안) AND (경사 ≤ 25°) AND (피폭예산 내)
```

- **HARD 게이트 = 하드 제약(잠금).** 복귀선 밖·급경사·피폭초과 셀은 **생명점수가 100이어도** 추천 안 함 → 회색 + 사유 표시, go 버튼 비활성.
- **SOFT 게이트 = 감점/가중.** 경사·흙질은 체력 소모↑(Pandolf η=2.0), 통신음영은 보수적 감점.
- **복귀선이 왕.** 소모품이 줄면 반경이 수축 → 아까 추천되던 먼 고득점 지점이 자동으로 잠김. (산소 90%라도 너무 멀면 잠금, 20%라도 가까우면 통과 — 사용자가 말한 그 로직.)

### 왜 이 구조가 정답인가 (NASA 근거)

이건 NASA가 실제로 만드는 **PersEIDS**(Personalized EVA Informatics and Decision Support)와 같은 철학이다:
- PersEIDS = EVA 타임라인에 **소모품 사용을 자동 투영**하고, **실시간 확률적 안전평가**를 주며, **경로를 추천**하는 **의사결정 보조** 시스템. (NTRS 20230007488)
- 즉 시스템은 **추천·경고(advisory)**만 하고, 실행 판단은 사람이. MARSWALK도 동일.
- EVA DSS 연구 공통 결론: 도구는 계산을 떠안아 **운영자가 상위 판단에 집중**하게 하고, **안전·시간 트레이드오프를 여러 경로에 대해 동시 평가**해 제시. (SpaceCHI 2025, 10.4230/OASIcs.SpaceCHI.2025.25 · Miller & Feigh, Georgia Tech)

### 권한 원칙 (앱에 박을 규칙)

1. **앱은 보조.** 추천·경고·점수만 제공. 명령하지 않음.
2. **최종 go/no-go = 우주인.** 모든 추천은 우주인이 수용/기각 가능.
3. **안전 게이트는 끌 수 없음.** HARD 게이트 해제는 우주인의 **명시적 수동 확인**을 거쳐야(자동 무시 불가). 안전이 과학보다 항상 우선.

---

## 6. 개발 전달 체크리스트

- [ ] `data/weights.json` 읽어 지표·순위·ROC/RS 로드. UI는 **순위 드래그**로 재배열(숫자 직접입력 아님).
- [x] 각 셀 Sᵢ 채점 → 생명점수 히트맵 — **S1·S2 실데이터로 구현**(`build_grid.py`), 전 칸 score 채움.
- [ ] 안전 레이어는 **점수에 합산 금지.** 게이트로만 사용.
- [ ] 잠긴 셀: 회색 + 사유("복귀선 밖" 등) + go 비활성.
- [ ] 복귀선 반경은 소모품 모델(§4, 모델스펙)과 실시간 연동.
- [x] `grid.js` 전처리: DEM slope + CRISM(S1) + SIM3464(S2). **완료.** (잔여: S5 투입; S4 물활동·S3 염류는 설계완료·비적용)

---

## 7. 근거 출처 (이 문서)

- **iMOST** — Des Marais et al. (2018) "Seeking the Signs of Life", NTRS 20180003291 — https://ntrs.nasa.gov/api/citations/20180003291/downloads/20180003291.pdf
- **Hartz & George (2022)** "Quantitative Framework for Astrobiology Strategies and in situ Biogenic Assessments" *Front. Astron. Space Sci.* 9:769607 — https://doi.org/10.3389/fspas.2022.769607
- **ExoMars Biosignature Score** — Torres, Sefton-Nash, Vago (2022) EPSC2022-912 — https://doi.org/10.5194/epsc2022-912
- **CoLD scale** — Green et al. (2021) "Call for a framework for reporting evidence for life beyond Earth" *Nature* 598:575-579 — https://doi.org/10.1038/s41586-021-03804-9
- **점토 보존** — McMahon et al. (2018) · Hickman-Lewis et al. (2025) *Nat. Commun.* 10.1038/s41467-025-57727-4 · Broz (2020) *Life* 10.3390/life10070113
- **ROC/RS 가중치** — Barron & Barrett (1996) *Management Science* 42(11):1515-1523 · Barron (1992) · Stillwell et al. (1981)
- **의사결정 보조(PersEIDS)** — NASA NTRS 20230007488 · Miller & Feigh (GT) · SpaceCHI 2025 (10.4230/OASIcs.SpaceCHI.2025.25)


---

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
| `S1..S5` | 생명점수 지표 0~4 | **S1=CRISM·S2=SIM3464 실데이터 반영**, S3~S5는 래스터 없으면 null |
| `score` | 생명점수 0~100 | **가용 지표만 재정규화**(지금 S1·S2 → 전 칸 채움) |

**정직성:** 래스터 안 주면 해당 Sᵢ는 `null`, score는 투입된 지표만으로 재정규화(가짜값 안 채움).

## 2. 실행

```bash
pip install rasterio numpy pyogrio shapely

# 최소(DEM만) → 경사 + 교신 활성, Sᵢ는 null
python build_grid.py --dem jezero_dem.tif --out grid.js --cell-px 8

# 풀(S1·S2 실데이터) — 현재 산출. S2 래스터는 make_s2.py로 SIM3464에서 먼저 생성
python make_s2.py                                 # → data/s2_jezero.tif
python build_grid.py --dem jezero_dem.tif \
       --crism zenodo_5575824/jezeroFinal.tif \
       --geo data/s2_jezero.tif --geo-scored \
       --out grid.js --clip-km 5 --cell-px 8 --antenna-h 15
```
- `--crism` : CRISM RGB 분류맵(3밴드) → 자동으로 범례 룩업(S1). `--geo --geo-scored` : 사전점수(0~4) 래스터 → footprint 평균(S2).
- `--cell-px` : 칸 하나 = DEM 몇 픽셀(실행 시 칸 크기 m 출력). 8px ≈ 160m. `--clip-km` : 기지 반경 클립. `--antenna-h` : 교신 가시선 안테나 높이(m).
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
- `S1`(CRISM 분류맵) = 범례 RGB **최근접색 분류 → 칸 footprint 최빈 광물**(퍼센타일 아님, 미식별·배경 제외). `S2`(SIM3464) = 유닛별 점수 footprint 평균. 연속형 래스터를 `--geo-scored` 없이 주면 기존 5~95퍼센타일 정규화 사용.
- 가중치(ROC)는 데이터 아님 — 순위 기반 공식값. score는 **가용 지표만 재정규화**(위 생명점수 상세설계 §1 참고).


---

# MARSWALK 모델 근거·출처 (2026-11-14)

> 생체·대사·방사선·지형 모델에 쓴 **모든 값의 출처.** 발표 Q&A("그 숫자 어디서?") 방어용.
> 값은 3종류로 분류: **🟩 실측 · 🟦 논문 공식/값 · 🟨 근거 있는 추정(교체 가능)**

---

## 0. 한눈에 — 값의 종류

| 종류 | 뜻 | 예 |
|---|---|---|
| 🟩 실측 | 로버/센서가 화성에서 직접 측정 | RAD 선량, 지형 피폭 차폐, 레골리스 물성 |
| 🟦 논문 공식/값 | 발표된 방정식·측정 평균 | Pandolf 식, VO₂peak, 지속가능 % |
| 🟨 근거 있는 추정 | 화성 직접측정 불가 → 논문 근거로 추정 | 지형계수 η, 산소통 용량 |

---

## 1. 대사율 — Pandolf 방정식 🟦

`M_W = 1.5·M + 2.0·(M+L)·(L/M)² + η·(M+L)·(1.5·v² + 0.35·v·G)`

- **NASA JSC가 EVA traverse 대사율에 실제 사용** (Mars Campaign Office 지원, JSC Rock Yard 현장 측정) — ntrs.nasa.gov/citations/20240001423
- 원 방정식: Pandolf, Givoni, Goldman (1977) J Appl Physiol 43(4):577-81
- 와트→kcal: ×0.01433 kcal/(W·min) · 산소 1L ≈ 5 kcal (20.9 kJ)

## 2. 생리 기준값 🟦

| 값 | 쓴 값 | 출처 |
|---|---|---|
| VO₂peak | 37.5(남)/42.1(여) ml/kg/min | ISS 승무원 평균 · ntrs.nasa.gov/citations/20220014309 |
| 지속가능 작업률 | VO₂peak의 30~40% (35% 사용) | 〃 |
| 선발 평균 나이 | 34 → HRmax=220−나이 | NASA 후보 평균 · ntrs.nasa.gov/citations/20240001630 |
| 체중 | 80 kg | 🟨 대원 입력값(패드28). 데모 기본값 |

## 3. 지형계수 η — 🟨→🟦 (레골리스 실측으로 근거 강화)

**쓸 값: η ≈ 2.0 (범위 1.8~2.1)**
- 화성 레골리스 실측 = 느슨한 미세 모래: Viking 밀도 1.0~1.3 g/cc·점착 0~3.7 kPa (NTRS 20200003046) / InSight 입자 0.06~0.2mm·점착 0~1 kPa (Delage 2017)
- 지형계수 표(Soule & Goldman 1972): 포장 1.0 … **느슨한 모래 2.1** → 화성 ≈ η 2.0
- 리뷰: Richmond·Potter·Santee (2015)

## 4. 방사선 🟩 (대부분 실측!)

| 값 | 쓴 값 | 출처 |
|---|---|---|
| 기준 선량 | 0.64 mSv/day | Curiosity RAD, Hassler 2014 Science |
| 지형 차폐 | 최대 ~19% 감소 | RAD 직접 관측 · Guo 2026 JGR Planets |
| 고도/대기 | 높을수록↑ | RAD 4년 실측 · Guo 2017 |

→ 고도↑→피폭↑, 지형차폐→피폭↓ 둘 다 RAD 실측. (차폐 최대 ~19~24%)

## 5. 피로/체력 — W'BAL (critical power) 🟦
- 지속시간 = critical power 쌍곡선, 곡률상수 W' — Coats 2003
- W'BAL: CP 초과 소모·이하 회복, 고갈=탈진 → 우리 체력 모델이 이 구조.

## 6. 교체 요약 (데모값 → 근거값)
| 항목 | 기존 | 교체 | 근거 |
|---|---|---|---|
| η | 1.5 | **2.0** | 레골리스≈모래 |
| 피폭 차폐 | 60% | **~20%** | RAD 실측 (Guo 2026) |
| 피로 | 선형 | **W'BAL** | Coats 2003 |

## 7. 발표 방어 한 줄
> "대사율은 NASA Pandolf 방정식, 생리값은 ISS 승무원 실측, 방사선 지형차폐는 Curiosity RAD 직접 관측(최대 19%), 지형계수는 Viking·InSight 레골리스 물성 기반, 피로는 W-prime 모델. 직접 측정 불가한 값(η·체중)만 논문 근거 추정, 전부 교체 가능."

---

## 8. 참고문헌 — 논문 제목 + 링크

**대사율 (Pandolf)**
- Pandolf KB, Givoni B, Goldman RF (1977) "Predicting energy expenditure with loads while standing or walking very slowly." J Appl Physiol 43(4):577-581 — https://journals.physiology.org/doi/10.1152/jappl.1977.43.4.577
- NASA JSC Crew State & Risk Model (IEEE EMBC 2024) — NTRS 20240001423 — https://ntrs.nasa.gov/citations/20240001423

**생리 기준값**
- ISS 승무원 EVA 유산소 능력 — NTRS 20220014309 — https://ntrs.nasa.gov/citations/20220014309
- "EVA Metabolic Rate Model: Metabolic Rate Estimated from Heart Rate" — NTRS 20210024317 — https://ntrs.nasa.gov/citations/20210024317
- Apollo EVA 대사율 234 kcal/hr — NTRS 19910001262 — https://ntrs.nasa.gov/citations/19910001262
- 우주인 demographics (나이 34) — NTRS 20240001630 — https://ntrs.nasa.gov/citations/20240001630
- 산소 1L≈5kcal — NTRS 20120003917 — https://ntrs.nasa.gov/citations/20120003917

**방사선**
- Hassler DM et al. (2014) "Mars' Surface Radiation Environment Measured with the Mars Science Laboratory's Curiosity Rover." Science 343 — https://www.science.org/doi/10.1126/science.1244797
- Guo J et al. (2026) "Influence of Mars Topography on Radiation Dose Detected by MSL." JGR Planets — https://doi.org/10.1029/2026JE009704
- Guo J et al. (2017) "Dependence of the Martian radiation environment on atmospheric depth." JGR Planets — https://arxiv.org/abs/1712.06987
- Khaksarighiri S et al. (2023) "Zenith-Angle Dependence of the Downward Radiation Dose Rate on the Martian Surface." JGR Planets — https://doi.org/10.1029/2022JE007644

**지형계수 η / 레골리스**
- Soule RG, Goldman RF (1972) "Terrain coefficients for energy cost prediction." J Appl Physiol 32(5):706-708 — https://journals.physiology.org/doi/abs/10.1152/jappl.1972.32.5.706
- Richmond PW, Potter AW, Santee WR (2015) "Terrain Factors for Predicting Walking and Load Carriage Energy Costs: Review and Refinement." JSHP 3(3) — https://jhp-ojs-tamucc.tdl.org/jhp/article/view/67
- Mars soil simulants 리뷰 (Viking 물성) — NTRS 20200003046 — https://ntrs.nasa.gov/citations/20200003046
- Delage P et al. (2017) "Mechanical Properties of Martian Regolith Simulants." Space Sci Rev — https://doi.org/10.1007/s11214-017-0339-7

**체력 (W′BAL / critical power)**
- Coats EM et al. (2003) "Intensity-dependent tolerance to exercise after attaining V̇O₂max in humans." J Appl Physiol 95(2):483-490 — https://journals.physiology.org/doi/10.1152/japplphysiol.01064.2002

**생명점수 프레임워크**
- iMOST · MSR SSTM · Sephton et al. · Conrad & Eigenbrode · Hartz & George (2022, Frontiers) · ExoMars Biosignature Score (EBS)

---

## 9. 심박 모델 — PhysioNet 실측 검증 ⭐
- **데이터:** PhysioNet 트레드밀 운동 테스트 — 992명, 57만 샘플 (심박·VO2·속도)
- **보정 결과:** `HR = 70.5 + 113.2·%VO2`  (R²=0.77)
- **검증:** 기존 데모값(70 + 116·%VO2)이 실측과 거의 일치 → **심박 모델이 실측으로 검증됨**
- HRmax(220−나이=186)로 캡, %VO2>1은 "지속 불가" 플래그
- 출처: Mongin, García Romero, Alvero Cruz (2021) PhysioNet, DOI 10.13026/7ezk-j442 — physionet.org/content/treadmill-exercise-cardioresp/
- 산출물: `data/synthetic_eva.json` (실측 보정 기반 EVA 시계열), `scripts/calibrate_hr.py`


---

# MARSWALK — 검증 데이터 RAW 다운로드 (2026-11-14)

> 실측/공개 데이터 전부 raw 다운로드 가능. 운영진 "데이터 어디?" → 이 링크로 증명.

## ✅ 심박 — PhysioNet (992명 실측, 이미 받음)
- 페이지: https://physionet.org/content/treadmill-exercise-cardioresp/
- AWS: `aws s3 sync --no-sign-request s3://physionet-open/treadmill-exercise-cardioresp/ ./`
- DOI: 10.13026/7ezk-j442 · 필드: time·Speed·HR·VO2·VCO2·RR·VE

## ✅ 방사선 RAD — NASA PDS (화성 표면 실측 선량)
- PDS-PPI: https://pds-ppi.igpp.ucla.edu/data/MSL-M-RAD-3-RDR-V1.0/
- 검색: https://search-pdsppi.igpp.ucla.edu/search/view/?id=pds://PPI/MSL-M-RAD-3-RDR-V1.0/DATA
- SPDF(cdaweb): https://cdaweb.gsfc.nasa.gov/ → MSL | MSL_RAD_OBS-L2
- 논문: Hassler 2014 Science DOI 10.1126/science.1244797

## ✅ POV 실사 — Perseverance (Mars2020 raw)
- 갤러리: https://mars.nasa.gov/mars2020/multimedia/raw-images/
- API: https://mars.nasa.gov/rss/api/?feed=raw_images&category=mars2020&feedtype=json
- 키 불필요 · 퍼블릭 도메인

## ✅ 지도·지형·광물 — Mars Trek
- 포털: https://trek.nasa.gov/mars/
- 제품: MOLA·HRSC(지형) / THEMIS(열) / Viking·CTX·HiRISE(광학) / CRISM(함수광물)

## ✅ 우주기상 — DONKI
- API: https://api.nasa.gov/DONKI/ (DEMO_KEY 또는 무료키)
- SEP·FLR·notifications

## ✅ 지질 — USGS
- 허브: https://astrogeology-usgs.hub.arcgis.com/pages/interactive-maps-mars
- Jezero: SIM3464 https://pubs.usgs.gov/publication/sim3464

---

## 논문값 (raw=논문/보고서, 다운 가능)
- Pandolf 1977: journals.physiology.org/doi/10.1152/jappl.1977.43.4.577
- 아폴로 PLSS 소모품: NTRS 19720019460 · 20150009506
- 레골리스: Delage 2017 DOI 10.1007/s11214-017-0339-7 · NTRS 20200003046
- 지형계수: Soule&Goldman 1972 · Richmond 2015

## 모델링 가정 (raw 없음 — "근거 기반 설계, 조정 가능"으로 표기)
- 생명점수 가중치 값 (순서는 프레임워크, 값은 우주인 조정)
- 방사선 장소보정 식 (방향은 실측, 식은 근사)
- 장비 무게 (대표값)


---

# MARSWALK 데이터 레퍼런스 (2026-11-14)

> 데이터별 **링크 / 쓰는 기능 / 따오는 법 / 저장 방법.** 외부 NASA 데이터 6계열. 필수 "3종"을 5종으로 초과 충족.

## 저장은 4가지 패턴
- **A. 스트리밍(저장0):** 베이스맵·과학 타일 — Leaflet이 Trek서버서 실시간
- **B. 격자 GeoJSON(전처리):** 경사·바위·생명점수 — Jezero 격자에 값 구움
- **C. 라이브/캐시 JSON:** DONKI — 라이브 또는 과거 1건 캐시
- **D. 상수·URL:** RAD, POV, 생체 — 코드/JSON에 박음

핵심: 보기 레이어(A)와 계산 레이어(B)를 섞지 않는다.

## 외부 NASA 데이터 6계열
1. **지형·경사** — Trek https://trek.nasa.gov/mars/ · MOLA+HRSC·Jezero DEM → `gdaldem slope` (저장 B)
2. **바위(암석 피복)** — THEMIS 열관성 **실데이터**(Zenodo 4931348, Edwards&Buz 2021) → `build_grid.py --rock`로 rock(0~1) 격자에 구움(낮은TI=모래, 높은TI=바위). A* 바위밭 우회 (저장 B)
3. **광학 베이스맵** — Trek · OpenPlanetary https://www.openplanetary.org/opmbasemaps (A)
4. **과학·생명·물흔적** — Trek(CRISM·염류) · USGS SIM3464 https://pubs.usgs.gov/publication/sim3464 → GeoJSON (A+B)
5. **우주기상·방사선** — DONKI https://api.nasa.gov/ · RAD(Hassler 2014) (C+D)
6. **POV 실사** — https://mars.nasa.gov/mars2020/multimedia/raw-images/ · Raw API (키X) (D)

## 데이터 안 쓰는 기능 (로직·입력·기기·시뮬)
- 산소·복귀 모델, 위치·방위 계산, 사용자 입력·설정, 기기(음성·버튼·캠), 시뮬(버디·통신)

## ⚠️ 결정 필요 6 (실데이터 없음 → 근사/시뮬)
1. 통신 음영 — DEM LOS 근사  2. 심박 — 시뮬  3. POV 조인 — 노두 사전매칭
4. 바위 단위 — HiRISE 디지타이즈  5. 초국지 — HiRISE 딥줌  6. DONKI 타이밍 — 지구기준 각주

## 필수요건: 전부 ✅ (3종→5종 초과, 데이터 때문에 못 하는 기능 0개)

## 생체 데이터 ⚠️
"다운받는 데이터셋" 아님. 우주인 실시간 생체 피드는 공개 없음 → NASA 논문 수치를 코드에 박음.
- 공식·값은 `모델근거_출처` 문서 참고. 심박 실시간값은 시뮬.

## 공식 챌린지 리소스 대조
- Mars Trek ✅ · USGS ✅ · Perseverance ✅ (공식 안) / OpenPlanetary·DONKI ➕ (추가, 문제없음)


---

# MARSWALK 결정 로그 (2026-11-14)

> NASA Space Apps 2026 · Challenge 10 (Interplanetary Survival Guide: Martian Map) · 팀 NAVIS

## 1. 정체성
화성 기지 대원용 EVA 도보 내비. 기지서 계획(패드) → 현장서 걷기(HUD). 목표: Jezero·Neretva 삼각주에서 생명흔적(biosignature) 샘플 확보.

## 2. 사람을 화성에 보내는 이유
로봇 수십 년째 탐사 → 그래도 사람 = 현장 실시간 판단·과학. MARSWALK = 그 대원을 더 오래·멀리·안전하게 과학하게 하는 도구. walk-back은 겁주기가 아니라 과학 시간을 지키는 장치.

## 3. 관제는 "화성 표면 기지 버디"
- 지구 관제 ❌ 편도 최대 ~22분, 왕복 ~44분 → 실시간 불가
- 화성 궤도 ❌ 패스 때만 교신 → 연속 감시 불가
- 표면 버디 ✅ 같은 지표라 지연 거의 0 + 계속 연결

## 4. 양면 구조
- 패드(관제·계획): 지도 4층·경로·산소예산·안전링·생체·우주기상·과학목표·교신
- HUD(현장, 최소): 산소·시간/방향/복귀 데드라인/경보/교신 상태
- 기준: "지금 안 보면 죽나?" → 그것만 HUD

## 5. 데이터 4층 + 산소
경사·지질·방사선·열 (실제 NASA, 필수 3층 초과 → 4층). 산소 = walk-back 엔진. 필수요건 5/5.

## 6. HUD 유형
컴바이너식 축약 HUD = 현실적 기본 / AR HUD = 비전. (헬멧 눈~유리 10cm라 윈드쉴드식 불가)

## 7. 동적 안전 반경 (turn-back line)
산소·지형·폭풍·통신 중 제일 빡빡한 값으로 반경 자동 계산, 걸을수록 좁아짐.
🟢 자유 / 🟡 주의 / 🔴 통제선. HUD=복귀선까지 카운트, 패드=반경 조절.


---

# MARSWALK 페이지별 데이터 검증 매니페스트 (2026-11-14)

> 패드 각 페이지 요소 → 데이터/모델 → 파일 → 근거 → 상태.
> ✅실측·검증 · 🟦논문 · 🔧계산 · 📱입력/UI · ⚠️근사/시뮬

## 홈
| 요소 | 데이터 | 파일 | 근거 | 상태 |
|---|---|---|---|---|
| 대원 2인 상태 | 생체 시뮬 | synthetic_eva.json | PhysioNet 992명 실측 | ✅ |
| 계획 시작 | UI | — | — | 📱 |

## ① 지점 고르기
| 요소 | 데이터 | 파일 | 근거 | 상태 |
|---|---|---|---|---|
| 지도·레이어 5종 | Trek 타일 + 격자 | layers.json·grid.js | trek.nasa.gov·Zenodo 4931348 | ✅ (경사·S1·S2·**암석(THEMIS 열관성)** 실데이터 — 열 레이어 충족) |
| 생명점수 격자 | S1 CRISM + S2 SIM3464 | grid.js | Zenodo 5575824·SIM3464 | ✅ 전 칸 100% |
| 가중치 3종 | 프레임워크 | weights.json | iMOST·SSTM·Barron ROC | 🟦 |
| 후보 순위 | 생명점수(격자 score) | grid.js | S1·S2 가용지표 재정규화 | ✅ |
| 근거 등급 | 출처 메타 | layers.json | CRISM=궤도·Perseverance=로버 | ✅ |
| 복귀 불가 표기 | walk-back | consumables.json | Pandolf+PLSS | ✅ |
| 지점 영상 | POV | spots.json | Perseverance 실사 | ✅ |

## ② 계획 세우기
| 요소 | 데이터 | 파일 | 근거 | 상태 |
|---|---|---|---|---|
| 우주기상 | DONKI | donki_sample.json | api.nasa.gov/DONKI | ✅ |
| 적재 선택 | 장비무게 | equipment.json | 대표값(입력) | 📱 |
| 산소 예산·복귀 시각 | 모델 | consumables.json | Pandolf+PLSS(아폴로) | 🟦 |

## ③ 경로 미리보기
| 요소 | 데이터 | 파일 | 근거 | 상태 |
|---|---|---|---|---|
| 장애물·통과불가 | DEM 경사 격자 | grid.js | Trek·경사임계 15~25° | ✅ (경사 실데이터; 바위 디지타이즈 ⚠️) |
| 복귀 불가 루트 | walk-back | consumables.json | Pandolf+PLSS | ✅ |

## ④ 출발 확인
| 점검·비상분기·HUD전송 | UI/운영 | — | — | 📱 |

## ⑤ 관제
| 요소 | 데이터 | 파일 | 근거 | 상태 |
|---|---|---|---|---|
| 대원 상태(산소·심박) | 모델 | synthetic_eva.json·crew_spec.json | PhysioNet 실측 R²=0.77 | ✅ |
| 소모율 감시 | 소모품 | consumables.json | 아폴로 PLSS | 🟦 |

## ⑥ 경보 대응
| 요소 | 데이터 | 파일 | 근거 | 상태 |
|---|---|---|---|---|
| 경보 내용 | DONKI | donki_sample.json | api.nasa.gov | ✅ |
| 선택지 피폭(X선 환산) | RAD | radiation.json | Hassler 2014 Science | ✅ |

## ⑦ 리포트
| 요소 | 데이터 | 파일 | 근거 | 상태 |
|---|---|---|---|---|
| 시료 핀 | POV | spots.json | Perseverance | ✅ |
| 누적 피폭 | RAD | radiation.json | Hassler 2014 + Guo 2026 | ✅ |

## 설정
| 대원 제원 | 입력 | crew_spec.json | NTRS·PhysioNet | ✅ |
| 장비 무게 | 입력 | equipment.json | 대표값 | 📱 |

---

## 데이터 파일 목록 (data/)
| 파일 | 내용 | 근거 |
|---|---|---|
| spots.json | 탐사 지점·POV | Perseverance |
| weights.json | 생명점수 가중치 | iMOST·SSTM |
| layers.json | 지도 레이어 5종 | Trek·USGS |
| consumables.json | EVA 소모품 4종 | 아폴로 PLSS |
| radiation.json | 피폭 상수 | RAD Hassler·Guo |
| crew_spec.json | 대원 제원 | NTRS·PhysioNet |
| equipment.json | 장비 무게 | 대표값 |
| donki_sample.json | 우주기상 | DONKI |
| synthetic_eva.json | 실측 보정 생체 시계열 | PhysioNet 992명 |

## 남은 TODO (격자 전처리)
- 경사·교신 격자(DEM) ✅ · 생명점수 격자 S1(CRISM)·S2(SIM3464) ✅ → `grid.js` 전 칸 100% 완료.
- S4(물 활동)·S3(염류) = 설계완료·비적용 (S4는 S1·S2에 반영, S3은 Jezero 희박). 남은 것: S5(로버 근접) 투입 → score 자동 재혼합.


---

