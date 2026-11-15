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
2. **바위(암석 피복)** — THEMIS 열관성 **실데이터**(Zenodo 4931348, Edwards&Buz 2021) → `build_grid.py --rock`로 rock(0~1) 격자에 구움. 낮은TI=모래, 높은TI=바위. A* 바위밭 우회 (저장 B)
3. **광학 베이스맵** — Trek · OpenPlanetary https://www.openplanetary.org/opmbasemaps (A)
4. **과학·생명·물흔적** — Trek(CRISM·염류) · USGS SIM3464 https://pubs.usgs.gov/publication/sim3464 → GeoJSON (A+B)
5. **우주기상·방사선** — DONKI https://api.nasa.gov/ · RAD(Hassler 2014) (C+D)
6. **POV 실사** — https://mars.nasa.gov/mars2020/multimedia/raw-images/ · Raw API (키X) (D)

## 데이터 안 쓰는 기능 (로직·입력·기기·시뮬)
- 산소·복귀 모델, 위치·방위 계산, 사용자 입력·설정, 기기(음성·버튼·캠), 시뮬(버디·통신)

## ⚠️ 결정 필요 6 (실데이터 없음 → 근사/시뮬)
1. 통신 음영 — DEM LOS 근사  2. 심박 — 시뮬  3. POV 조인 — 노두 사전매칭
4. ~~바위 단위 — HiRISE 디지타이즈~~ → ✅ **해결: THEMIS 열관성(Zenodo 4931348)으로 rock(0~1) 실데이터화**  5. 초국지 — HiRISE 딥줌  6. DONKI 타이밍 — 지구기준 각주

## 필수요건: 전부 ✅ (3종→5종 초과, 데이터 때문에 못 하는 기능 0개)

## 생체 데이터 ⚠️
"다운받는 데이터셋" 아님. 우주인 실시간 생체 피드는 공개 없음 → NASA 논문 수치를 코드에 박음.
- 공식·값은 `모델근거_출처` 문서 참고. 심박 실시간값은 시뮬.

## 공식 챌린지 리소스 대조
- Mars Trek ✅ · USGS ✅ · Perseverance ✅ (공식 안) / OpenPlanetary·DONKI ➕ (추가, 문제없음)
