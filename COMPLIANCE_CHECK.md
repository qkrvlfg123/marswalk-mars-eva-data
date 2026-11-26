# 라이선스, 출처 점검

> 점검일 2026-11-15. 대상은 team-navis 가 NASA Space Apps Challenge 2026 에 낸 작업의 두 저장소임: 메인 3D 데모(`team-navis/2026-11-nasa-space-apps-seoul`)와 데이터 파트(이 저장소). 팀 내부 운영 도구 `hackathon-kit` 은 산출물이 아니므로 참고로만 포함함.
> 점검 기준은 역대 Space Apps 공통 규정(오픈소스, 출처, 저작권, NASA 브랜딩)임. 2026년 공식 Participant Terms & Conditions 최신본과의 대조는 이 문서에 포함돼 있지 않음.
> 메인 3D 데모와 `hackathon-kit` 에 대한 내용은 점검 당시의 기록이고, 이 저장소 안에서는 다시 확인할 수 없음.

---

## 요약

| 구분 | 건수 |
|---|---|
| 위반 | 0건 |
| 확인 필요 | 7건 (이 중 W5 는 이후 반영함) |
| 통과 | 나머지 전부 |

위반 항목은 없음. 확인 필요 항목은 메타 정보 보완이나 공식 약관 대조 수준이고, 대부분 출처 자체는 문서화돼 있음.

### 확인 필요 7건

| # | 저장소 | 항목 | 내용 |
|---|---|---|---|
| W1 | 메인 | HUD 디자인 에셋, 로고 (OpenAI 이미지 생성) | 출처와 권리는 기재돼 있음(생성물은 사용자 소유). AI 생성 자산이라는 표기가 필요한 곳에 빠지지 않았는지 확인 대상 |
| W2 | 메인 | NASA Mark III GLB 를 받은 URL, 파일 버전 미기록 | 출처(NASA 3D Resources)와 조건(NASA 미디어 지침)은 명확함. 버전 메타만 기록되지 않음 |
| W3 | 메인 | 관제 패드의 Mars Trek 타일 레이어 ID, 이용 조건 | 기저 데이터는 NASA 퍼블릭 도메인임. 타일 상품 ID 만 확정되지 않음 |
| W4 | 메인 | sharp/libvips 가 LGPL-3.0 | 개발 전용이고 배포에 포함되지 않아 제품 라이선스와 충돌하지 않음. NOTICE 추가는 선택 |
| W5 | 데이터 파트 | Leaflet (BSD-2) 의존성 라이선스 명시 | 반영함. `docs/2_sources.md` §10 표에 Leaflet BSD-2-Clause 행을 추가함 |
| W6 | 공통 | 2026 공식 T&C 최신본 | 이 문서는 역대 공통 기준으로 점검함. 공식 최신본과의 대조가 남아 있음 |
| W7 | hackathon-kit | LICENSE 저작권자가 팀이 아닌 개인 계정 | 내부 도구라 문제 없음. 조직명으로 통일하려면 `team-navis` 로 바꿈(선택) |

AI 사용 내역: 코드는 Claude 보조로 작성했고, 메인 저장소의 HUD 에셋과 로고는 OpenAI 이미지 생성물임. EVOVA 3D 모델은 배포에서 제거돼, 점검 시점 배포본의 AI 생성 자산은 HUD 와 로고뿐임. 근거는 메인 저장소 `docs/REFERENCES.md` §4, §9.

---

## 점검 기준 6개

| # | 기준 | 메인 3D 데모 | 데이터 파트 | 근거 |
|---|---|---|---|---|
| 1 | 원본 코드의 오픈소스 라이선스 | 통과. MIT (루트 LICENSE) | 통과. MIT (루트 LICENSE) | 두 저장소의 `LICENSE` (OSI 승인 MIT, Copyright 2026 team-navis) |
| 2 | 외부 자료 라이선스가 자유 이용 또는 오픈소스 | 통과 (W4 개발 전용 LGPL) | 통과 | A, B 표 참조 |
| 3 | 출처 목록 완비 | 통과 | 통과 | 메인 `docs/REFERENCES.md`, `public/data/reference/SOURCES.json`. 데이터 파트 `docs/2_sources.md`, `docs/3_data_reference.md` |
| 4 | 저작권 위반물 (음악, 이미지, 폰트, 상표) | 없음 | 없음 | 음악, 동영상 0, 폰트 번들 0, 이미지는 전부 출처 기재 |
| 5 | NASA 브랜딩 오용 | 없음 (면책 문구 명시) | 없음 | `REFERENCES.md` 의 "no endorsement by NASA…implied" |
| 6 | 민감정보 노출 (키, 비밀번호, 이메일) | 없음 | 없음 | E 스캔 결과 |

---

## A. 코드 의존성 라이선스

### A-1. 메인 3D 데모 (`2026-11-nasa-space-apps-seoul`)

배포(런타임)에 포함되는 것:

| 패키지 | 버전 | 라이선스 | 상태 |
|---|---|---|---|
| three | 0.170.0 | MIT | 통과 |
| Draco decoder (동봉) | three r170 사본 | Apache-2.0 (`public/draco/LICENSE` 동봉) | 통과 |
| Leaflet (관제 패드) | 1.9.4 | BSD-2-Clause | 통과 |
| Inter 폰트 | Google Fonts 런타임 | SIL OFL 1.1 | 통과 |

빌드, 테스트 전용 (배포에 포함되지 않음):

| 패키지 | 라이선스 | 상태 |
|---|---|---|
| vite | MIT | 통과 |
| @gltf-transform/cli | MIT | 통과 |
| playwright-core | Apache-2.0 | 통과 |
| sharp / @img/sharp-libvips-* | LGPL-3.0-or-later | 확인 필요 W4. 개발 전용, 배포 번들에 없음(약한 카피레프트, 제품과 충돌 없음) |

`package-lock.json` 집계: MIT 248, Apache-2.0 27, LGPL-3.0-or-later 18 (전부 sharp/libvips), ISC 11, BlueOak-1.0.0 5, CC0-1.0 2, BSD-3-Clause 2, CC-BY-3.0 1, BSD-2-Clause 1, 0BSD 1. GPL, AGPL, SSPL 같은 강한 카피레프트는 0건.

### A-2. 데이터 파트 (이 저장소)

버전을 고정한 의존성 파일은 없음. 루트 `README.md` 의 실행 방법과 스크립트 주석 기준이며 전처리 전용임(배포 산출물 아님).

| 패키지 | 라이선스 | 상태 |
|---|---|---|
| rasterio | BSD-3-Clause | 통과 |
| numpy | BSD-3-Clause | 통과 |
| pyogrio | MIT/BSD | 통과 |
| shapely | BSD-3-Clause | 통과 |
| pandas | BSD-3-Clause | 통과 |
| requests | Apache-2.0 | 통과 |

배포 산출물(`grid.js`, `grid.geojson`, HTML)은 데이터와 직접 작성한 코드임. 런타임 외부 의존성은 Leaflet (BSD-2-Clause) 하나이고 `marswalk_grid_demo.html` 의 `<head>` 에서 CDN 으로 불러옴. 버전은 고정돼 있지 않음.

---

## B. 에셋 파일 목록과 출처

### B-1. 메인 3D 데모

| 유형 | 파일, 수량 | 출처, 라이선스 | 상태 |
|---|---|---|---|
| 3D 모델 | `public/models/nasa/mark-iii-spacesuit.glb` | NASA 3D Resources, NASA 미디어 지침(퍼블릭) | 통과 (버전 메타는 W2) |
| 3D 모델 | eva/operator/rover (EVOVA), 사용하지 않음 | 2026-11-15 제거, `.gitignore` | 통과 (배포에 없음. Mark III 와 절차적 폴백으로 대체, 라이브 확인) |
| 3D 메시 (지형) | Hazcam/Navcam terrain mesh | NASA/JPL-Caltech PDS (퍼블릭) | 통과. `SOURCES.json` |
| 텍스처 7개 | `public/textures/polyhaven/` | Poly Haven CC0 1.0 | 통과. `LICENSES.json` |
| HUD 에셋 20개 | `public/assets/hud/*.webp` | OpenAI 이미지 생성 (생성물은 사용자 소유, OpenAI Terms) | 확인 필요 W1 (출처는 기재됨) |
| 로고 | `pad/assets/logo.png` (Areographic) | 팀 자체 제작 (OpenAI 생성). NASA 로고 아님 | 통과 |
| 기준 이미지 | PIA26368, PIA26640 | NASA/JPL-Caltech (크레딧 기재) | 통과 |
| 그 외 이미지 약 187개 | `docs/captures/*` | 팀 앱의 스크린샷 (제3자 권리 없음) | 통과 |
| 폰트 | 번들 0 (Inter 는 Google Fonts, OFL) | 해당 없음 | 통과. 배포 제한 폰트 없음 |
| 사운드, 동영상 | 0 | 해당 없음 | 통과 |

### B-2. 데이터 파트

| 유형 | 수량 | 상태 |
|---|---|---|
| 이미지, 3D, 폰트, 사운드, 동영상 번들 | 0 | 통과. 저작권 매체 자산 없음 |
| `data/` | 12개 (JSON, JS, `s2_jezero.tif`) | 통과. 데이터와 코드이고 미디어가 아님 |
| POV 실사 (런타임에 외부에서 로드) | Perseverance raw images URL (`data/spots.js`, `data/spots.json`, `data/pov_candidates.json`, 데모 HTML 인라인) | 통과. NASA/JPL, `docs/3_data_reference.md` 의 6번 항목에 기재 |

---

## C. 데이터 출처 대조

| 데이터 | 쓰임 | 출처 문서 | 라이선스 | 상태 |
|---|---|---|---|---|
| DEM (CTX, HiRISE 지형) | 경사, 교신, 3D 지면 | `docs/2_sources.md` §10. 메인 `REFERENCES.md` §3.1~3.2 | NASA, USGS 퍼블릭 도메인 | 통과 |
| CRISM 광물맵 | S1 생명점수 | `docs/2_sources.md` §8, §10 | CC-BY-4.0 (Zenodo 5575824) | 통과 |
| THEMIS 열관성 | 암석 피복 rock | `docs/2_sources.md` §8, §10 | CC-BY-4.0 (Zenodo 4931348) | 통과 |
| SIM 3464 지질도 | S2 생명점수 | `docs/2_sources.md` §8, §10 | USGS 퍼블릭 도메인 | 통과 |
| RAD 피폭 상수 | 선량 모델 | `docs/2_sources.md` §4, §8 | NASA 문헌 | 통과 |
| DONKI 우주기상 | SPE 폭풍 | `docs/2_sources.md` §10, `docs/3_data_reference.md` | NASA 퍼블릭 | 통과 |
| Perseverance POV, 위치 | 지점 영상, 핀 | `docs/3_data_reference.md`, `docs/5_page_verification.md` | NASA/JPL (JPL image policy) | 통과 |
| PhysioNet 심박 | 생체 보정 | `docs/2_sources.md` §9 | Contributor Review Health Data License 1.5.0 (인용 필수, 기재됨) | 통과. 원본은 저장소에 없음 |
| OpenPlanetary 베이스맵 | 지도 타일 | `docs/2_sources.md` §10 | 공개 타일 (기저 데이터는 NASA/USGS 퍼블릭) | 통과 |
| Mars Trek 타일 | 지도 타일 | `docs/2_sources.md` §10. 메인 `REFERENCES.md` §6.1 | NASA 퍼블릭 | 통과 (메인 패드 타일 ID 는 W3) |

출처가 빠진 데이터는 없음.

---

## D. LICENSE 와 README

| 저장소 | LICENSE | README 의 데이터 출처, 라이선스 안내 | 상태 |
|---|---|---|---|
| 메인 3D 데모 | MIT (루트) + 구성요소별 (draco Apache-2.0, polyhaven CC0) | `## 라이선스` 절 + `docs/REFERENCES.md` | 통과 |
| 데이터 파트 | MIT (루트) | `## 출처`, `## 라이선스` 절 + `docs/2_sources.md` §10 라이선스 표 | 통과 |
| hackathon-kit | MIT (저작권자 표기는 W7) | 내부 도구 | 통과 (W7 확인 필요) |

---

## E. 민감정보 스캔

| 패턴 | 메인 | 데이터 파트 | 결과 |
|---|---|---|---|
| API 키, 토큰 (`AKIA`, `ghp_`, `sk-`, `api_key=`, `token=`) | 없음 | 없음 | 통과 |
| 비밀번호, 개인키 (`password=`, `BEGIN PRIVATE KEY`) | 없음 | 없음 | 통과 |
| 개인 이메일, 전화번호 | 없음 | 없음 | 통과 |
| `.env`, credential 파일 | `.gitignore` 로 제외 (`.env`, `*.key`, `*.pem`) | 해당 파일 없음 | 통과 |

데이터 파트의 `scripts/check_apis.py` 에는 NASA API 의 공개 데모 키 문자열(`DEMO_KEY`)만 들어 있고 개인 키는 없음. 이 스크립트의 URL 에 `api_key=` 가 나오지만 값은 그 공개 데모 키임.

---

## NASA 브랜딩 상세 (기준 5)

- NASA 인시그니아(미트볼), 로고타입(웜), NASA Seal 이미지는 0건임(png, svg, jpg, glb 파일명 전수 확인).
- `pad/assets/logo.png` 는 팀 자체 브랜드 "Areographic" (산, 지구, 화성 사구, 궤도) 이고 NASA 로고가 아님.
- `mark-iii-spacesuit.glb` 는 NASA 3D Resources 의 우주복 모델임(로고가 아니고 크레딧을 기재함).
- 후원, 승인, 협력을 뜻하는 표현은 0건임. 메인 `REFERENCES.md` §10 에 비보증 문구가 명시돼 있음.
- "NASA/USGS 데이터 사용" 같은 사실적 출처 표기만 씀. 규정이 허용하는 범위임.

---

## 남은 확인 사항

- 이 문서의 규정 기준은 역대 Space Apps 공통 기준(오픈소스, 출처, 저작권, NASA 브랜딩)임. 2026년 공식 Participant Terms & Conditions 최신본(spaceappschallenge.org 의 해당 연도 약관)과의 대조가 남아 있음. 해마다 바뀔 수 있는 부분은 (a) 요구하는 오픈소스 라이선스 범위, (b) AI 생성물 사용과 표기 규정, (c) NASA 자산 사용 세칙임.
- 메인 3D 데모의 자산 출처 상세와 미확정 항목은 그 저장소 `docs/REFERENCES.md` §7 (출처 누락, 이용 조건 미확인 목록)에 정리돼 있음.
- 라이선스 판단이 불명확한 항목은 위반이 아니라 확인 필요로 분류함.
