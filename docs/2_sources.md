# MARSWALK 모델 근거·출처 (2026-11-15)

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
| 적재 하중 L(공구+시료통) | 20 kg 기본(0~50 범위) | 🟦 Apollo 지질공구 총질량 22.9~53.0 kg — Allton 1989 JSC-23454 |

**적재 하중 L — `data/equipment.json` 🟨→🟦**
Pandolf 식의 L = 체중 외에 **몸 밖으로 지고/메고 다니는 하중**(공구·시료 수납통·백팩/PLSS). 수트 착용 무게는 넣지 않음.
- 공구 캐리어 HTC 13.4 kg · 시료통 ALSRC '록박스'(빈) 6.7 kg — Allton 1989, JSC-23454
- 임무별 지질공구 총질량(공구+용기): A11 22.9 · A12 29.2 · A14 34.1 · A15 50.3 · A16 53.0 · A17 45.7 kg — 같은 카탈로그. 데모 기본 L 20 kg ≈ Apollo 11 수준, 슬라이더 0~50은 A11~A16 범위 포괄.
- 참고 PLSS 질량: 제어부 포함 ~47 kg(104 lb), 본체 단독 ~38 kg(84 lb) — NASA Apollo Lunar Surface Journal. PLSS까지 L에 넣는 고하중 시나리오용.

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
| 적재 하중 L | 대표값 20kg | **Apollo 실측 22.9~53.0kg** | Allton 1989 JSC-23454 |
| 암석 피복 rock | (없음) | **THEMIS 열관성 실데이터 → 0~1** | Edwards & Buz 2021 (Zenodo 4931348) |

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

**적재 하중 L (공구·시료통·PLSS)**
- Allton JH (1989) "Catalog of Apollo Lunar Surface Geological Sampling Tools and Containers." NASA JSC-23454 (LESC-26676), Lyndon B. Johnson Space Center — https://www.lpi.usra.edu/captem/lsac/alltonLunarToolCatalog.pdf (HTC 13.4 kg · ALSRC 6.7 kg · 임무별 공구총질량 22.9~53.0 kg)
- NASA Apollo Lunar Surface Journal — Portable Life Support System (PLSS ~47 kg 제어부 포함 / ~38 kg 본체) — https://www.nasa.gov/wp-content/uploads/static/history/alsj/

**생명점수 데이터셋 (S1 CRISM · S2 지질)**
- S1 CRISM 광물맵 — Parente M, Saranathan AM, Itoh Y, Tarnas JD, Seelos FP, Mustard JF, "Map of the dominant mineralogy over and around the Mars2020 landing ellipse with correspondent spectral signatures", Zenodo 5575824 — https://doi.org/10.5281/zenodo.5575824 · **라이선스 CC-BY-4.0** (방법 논문: Itoh & Parente 2021 · Saranathan & Parente 2021)
- S2 지질맵 — Sun VZ & Stack KM (2020) "Geologic map of Jezero crater and the Nili Planum region, Mars", USGS SIM 3464 — https://doi.org/10.3133/sim3464 · **라이선스: 미국 정부 저작물 → 퍼블릭 도메인**(출처 표기 권장)

**암석 피복 / 열관성 (rock layer — 안전·A* 우회)**
- Edwards CS & Buz J (2021) "THEMIS-derived Thermal Inertia of Jezero Crater, Mars." Zenodo 4931348 — https://doi.org/10.5281/zenodo.4931348 · **라이선스 CC-BY-4.0** (단위 J·m⁻²·K⁻¹·s⁻¹ᐟ², null=0)
- 기준값: ~150 느슨한 모래 / 350 굳은(indurated) 퇴적암 / >1200 결정질 화성암 → rock(0~1) 2구간 선형 매핑(150→350=0→0.5, 350→1200=0.5→1.0)
- 해석 근거: Mellon et al. 2000(TPS 열관성) · Fergason et al. 2006(THEMIS TI) · Edwards & Buz 2021(Jezero TI 맵)

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
- 데이터셋: Mongin D, García Romero J, Alvero Cruz JR (2021) "Treadmill maximal exercise tests from the Exercise Physiology and Human Performance Lab of the University of Malaga" (v1.0.1), PhysioNet, DOI 10.13026/7ezk-j442 — physionet.org/content/treadmill-exercise-cardioresp/
  - **라이선스: PhysioNet Contributor Review Health Data License 1.5.0** (재배포 시 라이선스 표기 필수)
  - 원 논문: Mongin et al. (2021) *Research in Sports Medicine*, DOI 10.1080/15438627.2021.1954513
  - **표준 플랫폼 인용:** Pollard TJ, et al. (2026) "PhysioNet as a global platform for biomedical research." *Nature Health*.
- 산출물: `data/synthetic_eva.json` (실측 보정 기반 EVA 시계열), `scripts/calibrate_hr.py`

---

## 10. 데이터셋 라이선스 & 저작자 표기 (재배포·발표 시 준수)

> 각 외부 데이터 출처별 라이선스와 attribution. Zenodo 레코드 `License` 필드 실확인(둘 다 **CC-BY-4.0**), PhysioNet은 데이터셋 페이지 라이선스.

| 데이터셋 | 라이선스 | 저작자 표기(attribution) |
|---|---|---|
| **CRISM 광물맵** (Zenodo 5575824) | **CC-BY-4.0** | Parente, Saranathan, Itoh, Tarnas, Seelos, Mustard (2021) |
| **THEMIS 열관성** (Zenodo 4931348) | **CC-BY-4.0** | Edwards & Buz (2021) |
| **USGS SIM3464 지질맵** | 미국 정부 저작물 → **퍼블릭 도메인** | Sun & Stack (2020), USGS (출처 표기 권장) |
| **Jezero DEM / Mars Trek 타일** | NASA·USGS → **퍼블릭 도메인** | NASA/JPL-Caltech · USGS Astrogeology |
| **MSL RAD 선량** (PDS) | NASA → **퍼블릭 도메인** | NASA/JPL · Hassler et al. (2014) |
| **DONKI 우주기상** | NASA Open Data → **퍼블릭 도메인** | NASA/CCMC |
| **Perseverance raw 이미지** | NASA → **퍼블릭 도메인** | NASA/JPL-Caltech/ASU |
| **OpenPlanetary 베이스맵** | 공개 타일 서비스(기저 데이터 NASA/USGS 퍼블릭 도메인) | OpenPlanetary · NASA/USGS |
| **PhysioNet 트레드밀 심박** | **PhysioNet Contributor Review Health Data License 1.5.0** | Mongin, García Romero, Alvero Cruz (2021) |

**준수 요약**
- **CC-BY-4.0**(CRISM·THEMIS): 재사용 시 저작자·출처·라이선스 링크(https://creativecommons.org/licenses/by/4.0/) 표기 + 변경 여부 명시.
- **NASA/USGS 퍼블릭 도메인**: 저작권 제한 없음. 관례상 "courtesy NASA/JPL-Caltech"·"USGS" 출처 표기.
- **PhysioNet (Contributor Review Health Data License 1.5.0)**: 데이터셋 재배포 시 라이선스 전문·DOI 동반. 표준 인용은 **Pollard et al. (2026, *Nature Health*)** + 데이터셋 저자(Mongin et al. 2021).
- 본 repo의 격자 산출물(`grid.geojson`·`grid.js`·`data/s2_jezero.tif`)은 위 소스를 가공한 2차물 — 배포 시 원 소스 라이선스(특히 CC-BY attribution) 승계.
