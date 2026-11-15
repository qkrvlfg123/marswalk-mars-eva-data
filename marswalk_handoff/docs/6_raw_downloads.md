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

## ✅ 암석 피복(열관성) — Zenodo 4931348 (이미 받음)
- 페이지: https://doi.org/10.5281/zenodo.4931348 (Edwards & Buz 2021, "THEMIS-derived Thermal Inertia of Jezero")
- 파일: `Jezero_Thermal_Inertia_v1.tiff` (1.72MB, GeoTIFF, 단위 J·m⁻²·K⁻¹·s⁻¹ᐟ², null=0, MD5 53fec7c990a90629e98c871a7a0da474)
- 받기: `curl -L -o Jezero_Thermal_Inertia_v1.tiff https://zenodo.org/api/records/4931348/files/Jezero_Thermal_Inertia_v1.tiff/content`
- 쓰임: `build_grid.py --rock` → rock(0~1) 격자(바위밭 A* 우회). 재현 시 `zenodo_4931348/`에 둠.

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
