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
