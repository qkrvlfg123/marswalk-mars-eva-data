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
