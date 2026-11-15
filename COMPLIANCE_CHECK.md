# COMPLIANCE_CHECK — NASA Space Apps 2026 제출 전 규정·라이선스 점검

> 점검일 **2026-11-15** · 대상: team-navis 제출물 = **메인 3D 데모**(`team-navis/2026-11-nasa-space-apps-seoul`) + **데이터 파트**(`team-navis/marswalk`, 이 repo). 내부 운영 툴 `hackathon-kit`은 제출 산출물이 아니므로 참고로만 포함.
> 판단 기준은 **역대 Space Apps 공통 규정**(오픈소스·출처·저작권·NASA 브랜딩). 2026 공식 Participant Terms & Conditions 최신본은 **사람이 한 번 눈으로 확인**할 것(리포트 끝 메모).

---

## 제출 가능 여부 요약

| 구분 | 건수 |
|---|---|
| ❌ **위반(하드 블로커)** | **0건** |
| ⚠️ **확인 필요(사람 확인)** | **7건** |
| ✅ 통과 | 나머지 전부 |

**→ 현재 ❌(하드 위반) 0건. 제출 가능 상태.** 단 아래 ⚠️는 제출 양식 작성·행정 확인 수준이며, 대부분 "이미 문서화됨 + 최종 확인만 남음"입니다.

### 제출 전 반드시 처리할 것 (행정)
1. **제출 양식 AI 사용 칸 작성** — 코드=Claude 보조, HUD 에셋·로고=OpenAI 이미지 생성. (EVOVA 3D 모델은 배포에서 제거됨 → 현재 배포본 AI 생성 자산은 HUD·로고뿐) · 근거 `docs/REFERENCES.md` §4·§9 (메인 repo)
2. **2026 공식 Participant T&C 최신본 1회 확인** — 아래 ⚠️W6.
3. (선택) **메인 repo 자잘한 메타 보완** — Mark III GLB 버전 기록(W2), Mars Trek 타일 ID(W3). 출처 자체는 이미 명확.

### ⚠️ 확인 필요 7건 (요약)
| # | repo | 항목 | 왜 ⚠️인가 |
|---|---|---|---|
| W1 | 메인 | HUD 디자인 에셋·로고(OpenAI 생성) | 출처·권리 기재됨(output 사용자 소유). **제출 AI 사용 칸 기재**만 확인 |
| W2 | 메인 | NASA Mark III GLB 받은 URL·파일 버전 미기록 | 출처(NASA 3D Resources)·조건(NASA 미디어지침)은 명확, **버전 메타만** 미기록 |
| W3 | 메인 | 관제 패드 Mars Trek 타일 레이어 ID·이용조건 | NASA 퍼블릭 도메인 기저, **타일 상품 ID만** 미확정 |
| W4 | 메인 | sharp/libvips = LGPL-3.0 | **dev 전용·미배포**라 제품 라이선스 충돌 없음. NOTICE 한 줄은 선택 |
| W5 | marswalk | Leaflet(BSD-2) 의존성 라이선스 명시 | 출처는 적혀 있고 BSD-2는 자유. `2_sources.md`에 라이선스명 한 줄 보완(선택) |
| W6 | 공통 | 2026 공식 T&C 최신본 | 규정 문구는 역대 공통 기준으로 점검 → **공식 최신본 사람 확인 필수** |
| W7 | hackathon-kit | LICENSE 저작권자 = `currenjin`(개인) | 내부 툴이라 무방. org 통일 원하면 `team-navis`로 변경(선택) |

---

## 6개 기준 체크리스트

| # | 기준 | 메인 3D 데모 | marswalk | 근거 |
|---|---|---|---|---|
| 1 | **원본 코드 오픈소스 라이선스** | ✅ MIT(루트 LICENSE) | ✅ MIT(루트 LICENSE) | 두 repo `LICENSE` (OSI 승인 MIT, Copyright 2026 team-navis) |
| 2 | **외부 자료 라이선스 자유/OSS** | ✅ (⚠️W4 dev-only LGPL) | ✅ | A·B 표 참조 |
| 3 | **References 출처 완비** | ✅ | ✅ | `docs/REFERENCES.md`·`public/data/reference/SOURCES.json` / `docs/2_sources.md`·`3_data_reference.md` |
| 4 | **저작권 위반물(음악/이미지/폰트/상표)** | ✅ 없음 | ✅ 없음 | 음악·동영상 0, 폰트 번들 0, 이미지 전부 출처 기재 |
| 5 | **NASA 브랜딩 오용** | ✅ 없음(면책 명시) | ✅ 없음 | `REFERENCES.md` "no endorsement by NASA…implied" |
| 6 | **민감정보 노출(키/비번/이메일)** | ✅ clean | ✅ clean | E 스캔 결과 |

---

## A. 코드 의존성 라이선스

### A-1. 메인 3D 데모 (`2026-11-nasa-space-apps-seoul`)
**배포(런타임)에 실제 포함:**
| 패키지 | 버전 | 라이선스 | 상태 |
|---|---|---|---|
| three | 0.170.0 | MIT | ✅ |
| Draco decoder(동봉) | three r170 사본 | Apache-2.0 (`public/draco/LICENSE` 동봉) | ✅ |
| Leaflet (관제 패드) | 1.9.4 | BSD-2-Clause | ✅ |
| Inter 폰트 | Google Fonts 런타임 | SIL OFL 1.1 | ✅ |

**빌드·테스트 전용(미배포):**
| 패키지 | 라이선스 | 상태 |
|---|---|---|
| vite | MIT | ✅ |
| @gltf-transform/cli | MIT | ✅ |
| playwright-core | Apache-2.0 | ✅ |
| sharp / @img/sharp-libvips-* | **LGPL-3.0-or-later** | ⚠️ W4 — dev 전용, 배포 번들 미포함(약한 카피레프트, 제품 충돌 없음) |

`package-lock.json` 집계: MIT 248 · Apache-2.0 27 · LGPL-3.0-or-later 18(전부 sharp/libvips) · ISC 11 · BlueOak-1.0.0 5 · CC0-1.0 2 · BSD-3-Clause 2 · CC-BY-3.0 1 · BSD-2-Clause 1 · 0BSD 1. **GPL/AGPL/SSPL 등 강한 카피레프트 0건.**

### A-2. marswalk (데이터 파트, 이 repo)
핀된 의존성 파일 없음 — `README.md` L47·스크립트 주석 기준(전처리 전용, **배포 산출물 아님**):
| 패키지 | 라이선스 | 상태 |
|---|---|---|
| rasterio | BSD-3-Clause | ✅ |
| numpy | BSD-3-Clause | ✅ |
| pyogrio | MIT/BSD | ✅ |
| shapely | BSD-3-Clause | ✅ |
| pandas | BSD-3-Clause | ✅ |
| requests | Apache-2.0 | ✅ |
배포 산출물(`grid.js`/`grid.geojson`/HTML)은 데이터·순수 코드. 런타임 외부: Leaflet(BSD-2, `marswalk_grid_demo.html` L6-7, ⚠️W5 라이선스명 보완 선택).

---

## B. 에셋 파일 목록·출처

### B-1. 메인 3D 데모
| 유형 | 파일/수량 | 출처·라이선스 | 상태 |
|---|---|---|---|
| 3D 모델 | `public/models/nasa/mark-iii-spacesuit.glb` | NASA 3D Resources · NASA 미디어지침(퍼블릭) | ✅ (버전 메타 ⚠️W2) |
| 3D 모델 | ~~eva/operator/rover(EVOVA)~~ | **2026-11-15 제거·`.gitignore`** | ✅ (배포 미포함, Mark III+절차적 폴백 — 라이브 검증 완료) |
| 3D 메시(지형) | Hazcam/Navcam terrain mesh | NASA/JPL-Caltech PDS(퍼블릭) | ✅ `SOURCES.json` |
| 텍스처 ×7 | `public/textures/polyhaven/` | Poly Haven **CC0 1.0** | ✅ `LICENSES.json` |
| HUD 에셋 ×20 | `public/assets/hud/*.webp` | **OpenAI 이미지 생성**(output 사용자 소유, OpenAI Terms) | ⚠️ W1 (출처 기재됨·제출 AI칸 확인) |
| 로고 | `pad/assets/logo.png` (Areographic) | 팀 자체(OpenAI 생성) — **NASA 로고 아님** | ✅ |
| 기준 이미지 | PIA26368·PIA26640 | NASA/JPL-Caltech(크레딧 기재) | ✅ |
| 그 외 이미지 ~187 | `docs/captures/*` | 자팀 앱 스크린샷(제3자 권리 없음) | ✅ |
| 폰트 | **번들 0** (Inter=Google Fonts OFL) | — | ✅ 배포 제한 폰트 없음 |
| 사운드/동영상 | **0** | — | ✅ |

### B-2. marswalk
| 유형 | 수량 | 상태 |
|---|---|---|
| 이미지/3D/폰트/사운드/동영상 **번들** | **0** | ✅ 저작권 매체 자산 없음 |
| `data/` | 12개(JSON/JS + `s2_jezero.tif`) | ✅ 데이터·순수코드(미디어 아님) |
| POV 실사(런타임 외부 로드) | Perseverance raw images URL(`spots.js`·`pov_candidates.json`) | ✅ NASA/JPL, `3_data_reference.md` L19 기재 |

---

## C. 데이터 출처 대조 (요청 데이터셋 전부 기재 확인)

| 데이터 | 쓰임 | 출처 문서 | 라이선스 | 상태 |
|---|---|---|---|---|
| **DEM** (CTX/HiRISE 지형) | 경사·교신·3D 지면 | `2_sources.md` L145 / 메인 `REFERENCES.md` §3.1-3.2 | NASA·USGS 퍼블릭 도메인 | ✅ |
| **CRISM** 광물맵 | S1 생명점수 | `2_sources.md`(CRISM ×4) | CC-BY-4.0 (Zenodo 5575824) | ✅ |
| **THEMIS** 열관성 | 암석 피복 rock | `2_sources.md` L70 | CC-BY-4.0 (Zenodo 4931348) | ✅ |
| **SIM3464** 지질도 | S2 생명점수 | `2_sources.md`(SIM3464) | USGS 퍼블릭 도메인 | ✅ |
| **RAD** 피폭 상수 | 선량 모델 | `2_sources.md`(RAD ×8) | NASA 문헌 | ✅ |
| **DONKI** 우주기상 | SPE 폭풍 | `2_sources.md`(DONKI) | NASA 퍼블릭 | ✅ |
| **Perseverance** POV·위치 | 지점 영상·핀 | `3_data_reference.md` L19·`5_page_verification.md` | NASA/JPL(JPL image policy) | ✅ |
| **PhysioNet** 심박 | 생체 보정 | `2_sources.md` §9(×9) | Contributor Review Health Data License 1.5.0(인용 필수, 기재됨) | ✅ |
| **OpenPlanetary** 베이스맵 | 지도 타일 | `2_sources.md` L149 | 공개 타일(기저 NASA/USGS 퍼블릭) | ✅ |
| **Mars Trek** 타일 | 지도 타일 | `2_sources.md` L145 / 메인 `REFERENCES.md` §6.1 | NASA 퍼블릭 | ✅ (메인 패드 타일 ID ⚠️W3) |

**누락된 데이터 출처: 없음.**

---

## D. LICENSE·README

| repo | LICENSE | README 데이터 출처·라이선스 안내 | 상태 |
|---|---|---|---|
| 메인 3D 데모 | ✅ MIT(루트) + 구성요소별(draco Apache-2.0, polyhaven CC0) | ✅ `## 라이선스` 섹션 + `docs/REFERENCES.md` | ✅ |
| marswalk | ✅ MIT(루트) | ✅ `## 출처` + `docs/2_sources.md` §10 라이선스표 | ✅ |
| hackathon-kit | ✅ MIT (저작권자 `currenjin` ⚠️W7) | 내부 툴 | ✅/⚠️ |

---

## E. 민감정보 스캔

| 패턴 | 메인 | marswalk | 결과 |
|---|---|---|---|
| API 키/토큰(`AKIA`, `ghp_`, `sk-`, `api_key=`, `token=`) | 없음 | 없음 | ✅ clean |
| 비밀번호/개인키(`password=`, `BEGIN PRIVATE KEY`) | 없음 | 없음 | ✅ clean |
| 개인 이메일/전화(gmail·naver·010-…) | 없음 | 없음 | ✅ clean |
| `.env`/credential 파일 | `.gitignore`로 제외(`.env`, `*.key`, `*.pem`) | 해당 파일 없음 | ✅ |

> 커밋 공동작성자 표기(`noreply@anthropic.com`)와 세션 식별용 사용자 이메일은 민감정보 노출에 해당하지 않음(전자는 봇 주소, 후자는 repo에 미포함).

---

## NASA 브랜딩 상세 (기준 5)

- NASA 인시그니아(미트볼)·로고타입(웜)·NASA Seal 이미지 **0건**(png/svg/jpg/glb 전수 파일명 스캔).
- `pad/assets/logo.png` = 팀 자체 브랜드 **"Areographic"**(산+지구+화성 사구+궤도) — NASA 로고 아님.
- `mark-iii-spacesuit.glb` = NASA 3D Resources **우주복 모델**(로고 아님, 크레딧 기재).
- endorsement 표현: "NASA 후원/승인/협력" 등 **0건**. 오히려 메인 `REFERENCES.md` §10에 **비보증 문구 명시**.
- "NASA/USGS 데이터 사용" 식 **사실적 출처 표기만** 사용 — 규정 허용 범위.

---

## 참고 메모 (사람이 확인할 것)

- **본 리포트의 규정 기준은 역대 Space Apps 공통 기준**(오픈소스·출처·저작권·NASA 브랜딩)으로 점검한 것입니다. **2026 공식 Participant Terms & Conditions 최신본**(spaceappschallenge.org의 해당 연도 약관)을 제출 전 **사람이 1회 직접 대조**해 주세요 — 특히 (a) 요구 오픈소스 라이선스 범위, (b) AI 생성물 사용·표기 규정, (c) NASA 자산 사용 세칙이 해가 바뀌며 갱신될 수 있습니다.
- 메인 3D 데모의 자산 출처 상세·미확정 항목은 그 repo `docs/REFERENCES.md` §7(출처 누락·이용조건 미확인 목록)에 팀이 자체 신고한 TODO가 있으니 함께 확인하세요.
- 라이선스 판단이 애매한 항목은 모두 ❌가 아닌 ⚠️로 두었습니다(하드 위반 아님). 최종 판단·조치는 팀이 결정하세요.
