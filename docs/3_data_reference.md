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
