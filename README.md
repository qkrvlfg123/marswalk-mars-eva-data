# MARSWALK

화성 Jezero 크레이터 EVA(선외활동) 의사결정 보조 데모 — **"어디로 갈까"(생명점수) + "안전하게 다녀올 수 있나"(복귀선·경사·교신·피폭)**. 앱은 추천·경고만 하고 최종 go/no-go는 우주인이 판단(안전 최우선).

> 최신 갱신: **2026-11-15** — 생명점수가 S1·S2 **실데이터**로 채워져 전 칸 100% 커버리지.

---

## 생명점수 (Biosignature Score)

칸(cell)마다 과학지표 Sᵢ(0~4) 5개를 ROC 가중치로 가중합 → 0~100.

```
score = Σ(wᵢ·Sᵢ, 투입된 i) / Σ(wᵢ, 투입된 i) / 4 × 100     # 가용 지표만 재정규화, 가짜값 안 채움
```

| 지표 | 입력 (실데이터) | 상태 | 커버리지 |
|---|---|---|---|
| **S1** 함수/점토광물 | CRISM 광물맵 — Zenodo 5575824 (Parente·Itoh·Saranathan) | ✅ 실데이터 | 2,488/3,067 (81.1%) |
| **S2** 퇴적·델타 맥락 | USGS 지질맵 SIM3464 — Sun & Stack 2020 | ✅ 실데이터 | 3,067/3,067 (100%) |
| **S4** 물 활동 · **S3** 염류 | S1·S2에 내재 / Jezero 희박 | 🟦 **설계완료·비적용** | — |
| **S5** 로버 근접 | — | ⬜ **미투입(유일)** | — |

- **S4 물 활동·S3 염류 = 설계완료·비적용:** **S4 물 활동**은 S1(점토)·S2(델타)가 *둘 다 물로 형성·퇴적된 지표*라 이미 반영됨(별도 투입 시 이중계산). **S3 염류**는 Jezero가 염류 희박이라 해당 적음. 둘 다 루브릭·가중치(ROC)는 설계로 유지, Jezero엔 미투입. → 실제 '미투입'은 **S5(로버 근접) 하나.** (번호 규약: 코드 기준 S4=물활동 순위3·ROC .157, S3=염류 순위4·ROC .09)
- **score 커버리지 100%** (3,067칸) · min/평균/max = **25 / 42.7 / 100**.
- **Jezero floor = S2 1** — Perseverance 착륙 후 바닥이 화성암(Máaz/Séítah 화성암질)으로 확인돼 '퇴적'에서 하향. 델타 팬(Jezero fan) = S2 4.
- 데모 핀은 하드코딩이 아니라 **그 위치 격자 score(실데이터)** 를 읽음: 델타 전선 **84**, Cheyava 25, Hawksbill 25, Séítah ~30.

안전 레이어(경사 `slope_deg`, 교신 `comm`, **암석 피복 `rock`**)는 실데이터로 전 칸 채움 — 점수에 합산하지 않고 **게이트/우회로만** 사용. 경사·교신은 Jezero CTX DEM 20m(USGS), `rock`(0~1)은 THEMIS 열관성(Zenodo 4931348, Edwards&Buz 2021): 낮은 TI=모래→`rock`↓, 높은 TI=바위→`rock`↑. A* 경로가 간선비용 `×(1+2·rock)`로 **바위밭을 우회**.

---

## 재현 (파이프라인)

```bash
# 1) 지질맵 → S2 래스터 (SIM3464 GeoUnits_v1 폴리곤 → 유닛별 S2 0~4)
python make_s2.py                     # → data/s2_jezero.tif

# 2) 생명점수 격자 (S1 CRISM + S2 지질 + DEM 경사/교신)
python build_grid.py --dem jezero_dem.tif \
  --crism zenodo_5575824/jezeroFinal.tif \
  --geo data/s2_jezero.tif --geo-scored \
  --rock zenodo_4931348/Jezero_Thermal_Inertia_v1.tiff \
  --out grid.js --clip-km 5 --cell-px 8 --antenna-h 15
```

의존성: `pip install rasterio numpy pyogrio shapely`. 출력 `grid.js`(`window.GRID`) 를 `marswalk_grid_demo.html` 옆에 두면 지도 데모가 자동 로드.

---

## 📦 핸드오프 zip 내용물 (`marswalk_handoff.zip`) — 파일별 설명

> 압축 풀면 `marswalk_handoff/` 하위에 아래 구조. **대용량 원본(DEM·CRISM·SIM3464·PhysioNet)은 미포함** — 재현 시 `docs/6_raw_downloads.md` 링크로 받으세요.

**루트**

| 파일 | 이게 뭐다 |
|---|---|
| `README.md` | 이 문서 — 프로젝트 개요·생명점수·재현법·전체 파일 설명 |
| `marswalk_grid_demo.html` | Leaflet 지도 데모 — 경사 히트맵 + 생명점수 핀 + EVA 소모품/복귀선 시뮬. 옆의 `grid.js` 자동 로드 |
| `grid.js` | **최종 격자**(3,067칸, 칸≈160m, 기지 5km 클립) — `window.GRID` 전역. 데모가 직접 읽음 |
| `grid.geojson` | 동일 격자의 **순수 GeoJSON** — React/Leaflet 프론트에서 `fetch()`용 |

**docs/ — 설계·검증 문서(md)**

| 파일 | 이게 뭐다 |
|---|---|
| `1_model_spec_handoff.md` | 모델 6종(대사율·산소·복귀선·체력·심박·피폭) 공식·입출력·상수 — 개발 이식용 |
| `2_sources.md` | 모든 상수값의 출처(논문·실측) — Q&A 방어 |
| `3_data_reference.md` | 외부 NASA 데이터 6계열·저장 패턴(스트리밍/격자/캐시/상수) |
| `4_decision_log.md` | 설계 결정 로그(정체성·양면 UI·동적 복귀선) |
| `5_page_verification.md` | 패드 페이지별 요소→데이터→파일→근거→상태 매니페스트 |
| `6_raw_downloads.md` | **실측/원본 데이터 RAW 다운로드 링크** — 제외된 대용량 원본은 여기서 취득 |
| `7_biosignature_design.md` | 생명점수 상세 설계 — 지표 순위·ROC 가중치·S1/S2 루브릭·구현 현황 |
| `8_grid_guide.md` | `build_grid.py` 격자 전처리 가이드(속성·실행·앱 연동) |
| `9_verification_status.md` | 생명점수 격자 검증 현황 — 커버리지·score 분포·핀 4개 |
| `12_api_data_spec.md` | **데이터·API 계약서** — grid.geojson/data json 실제 필드·타입, 모델 함수 시그니처·상수, 런타임 흐름. React+Leaflet+Recharts+Zustand 이식용 |

**data/ — 앱 입력 데이터**

| 파일 | 이게 뭐다 |
|---|---|
| `weights.json` | 생명점수 지표·순위·ROC/RS 가중치(숫자는 Barron 공식 계산) |
| `spots.json` / `spots.js` | 탐사 지점(좌표·POV·메모). `.js`는 `window` 전역판 |
| `layers.json` | 지도 레이어 5종 정의(경사·지질·방사선·**열**·광학). 안전레이어에 `rock`(THEMIS 열관성) 포함 — 열 레이어 실데이터 충족 |
| `consumables.json` | EVA 소모품 4종(산소·냉각수·CO₂·배터리) 용량·소모 |
| `radiation.json` | 피폭 상수(RAD 0.64 mSv/day·지형차폐) |
| `crew_spec.json` | 대원 제원(체중·VO₂peak·나이) |
| `equipment.json` | 장비 무게(대표값) |
| `donki_sample.json` | 우주기상 샘플 이벤트(NASA DONKI) |
| `synthetic_eva.json` | PhysioNet 992명 실측 보정 생체 시계열 |
| `s2_jezero.tif` | **SIM3464→S2 래스터**(0~4, ~94KB). `build_grid.py --geo` 입력(델타·퇴적). 이것만 있으면 349MB 원본 없이 grid 재생성 가능 |

**scripts/ — 전처리/취득 스크립트(py)**

| 파일 | 이게 뭐다 |
|---|---|
| `build_grid.py` | ★최신. DEM 경사·교신 + CRISM(S1) + 지질(S2) → `grid.js`/`grid.geojson` |
| `make_s2.py` | USGS SIM3464 지질 폴리곤 → 유닛별 S2(0~4) 래스터 `data/s2_jezero.tif` |
| `calibrate_hr.py` | PhysioNet 실측으로 심박식 보정(HR=70.5+113.2·%VO2) + 합성 EVA 생성 |
| `gen_biosignature.py` | 생명점수 가중치 생성기(지표 순위→ROC/RS 숫자) → `weights.json` |
| `fetch_pov.py` | Perseverance raw 이미지(델타 POV) 수집 |
| `check_apis.py` / `check_datasets.py` | 외부 NASA API·데이터셋 접근 가능 점검 |

### 재현에 필요한 (zip 제외) 대용량 원본 — `docs/6_raw_downloads.md`

| 원본 | 놓을 경로(재현 시) | 출처 |
|---|---|---|
| Jezero CTX DEM 20m (~90MB) | `jezero_dem.tif` | USGS Astrogeology / Mars Trek |
| CRISM 광물맵 | `zenodo_5575824/jezeroFinal.tif` | Zenodo 5575824 |
| THEMIS 열관성 (~1.7MB) | `zenodo_4931348/Jezero_Thermal_Inertia_v1.tiff` | Zenodo 4931348 (Edwards & Buz 2021) |
| USGS SIM3464 지질맵 (~349MB) | `sim3464_extract/…/Nili.gdb` | USGS SIM 3464 |
| PhysioNet 트레드밀(심박 원본) | `physionet_data/` | PhysioNet 10.13026/7ezk-j442 |

> 프론트엔드만 돌릴 거면 원본 불필요 — `grid.js`/`grid.geojson`가 이미 최종 산출물. 원본은 격자를 **다시 만들 때**만 필요(단, S2는 `data/s2_jezero.tif`가 들어있어 SIM3464 원본 없이도 재생성 가능).

---

## 출처

- **S1** CRISM 광물맵 — Zenodo 5575824 — https://doi.org/10.5281/zenodo.5575824
- **S2** 지질맵 — Sun & Stack (2020) USGS SIM 3464 — https://doi.org/10.3133/sim3464
- **암석 피복(rock)** 열관성 — Edwards & Buz (2021) THEMIS Jezero TI — https://doi.org/10.5281/zenodo.4931348
- **보존 근거** — Broz (2020) *Life* 10.3390/life10070113 · iMOST (Des Marais 2018)
- 상세 설계·근거는 `marswalk_handoff/docs/` 참조.
