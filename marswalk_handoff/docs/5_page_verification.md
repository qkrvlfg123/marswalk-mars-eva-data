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
| 지도·레이어 5종 | Trek 타일 | layers.json | trek.nasa.gov | ✅(경사 격자 ⚠️) |
| 가중치 3종 | 프레임워크 | weights.json | iMOST·SSTM | 🟦 |
| 후보 순위 | 생명점수 | weights.json+spots.json | SSTM 가중합 | 🟦 |
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
| 장애물·통과불가 | DEM 경사+바위 | layers.json | Trek·경사임계 15~20° | ⚠️격자 전처리 |
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
- 경사 격자(DEM), 생명점수 격자(CRISM) → data/grid.geojson (현재 슬라이더/점수 근사)
