# MARSWALK 남은 작업

> 2026-11-14 작성, 2026-11-15 격자 산출 이후 상태로 갱신함. 저장소에는 데이터, 모델 문서, 지도 데모가 들어 있고 아래는 그 다음 단계의 작업임.

## 1. 앱 구현 (개발 전환 시 필수)

1. 앱 실제 구현: React + Leaflet + Recharts + Zustand.
   - 모델(대사율, 산소, 복귀선, 체력, 심박, 피폭, 생명점수)을 순수 함수로 이식함. 참조: `marswalk_grid_demo.html`, `docs/1_model_spec_handoff.md`, `docs/12_api_data_spec.md`.
   - 패드(계획)와 HUD(현장) 양면 UI.
2. `grid.geojson` 앱 연동: Leaflet GeoJSON 레이어로 경사, 교신을 색칠함.
   - 안전 게이트 적용: `slope_deg>25` 또는 복귀선 밖이면 잠금(회색), `comm=shadow` 이면 교신 경고(참고용).
   - 연동 예시: `docs/8_grid_guide.md` §5.

## 2. 데이터 보강 (선택)

3. 생명점수 지표 채우기.
   - 완료: S1(CRISM 광물맵), S2(USGS SIM 3464) 를 격자에 투입함. CRISM 은 범례 색 룩업, S2 는 사전 점수 래스터의 칸 평균으로 채점함. 1밴드 연속형 래스터를 넣을 때 쓰는 5~95 퍼센타일 정규화는 예시 수준이라 실제 단위에 맞춘 루브릭 고정이 필요함.
   - 남음: S5(로버 근접, Perseverance 트래버스) 레이어 투입. 투입하면 score 가 다시 혼합됨.
   - 남음: S1 미식별 칸 579개(커버리지 81.1%) 처리 방침. 현재는 보간하지 않고 비워 둠.
   - 재생성 명령: `python scripts/build_grid.py --dem jezero_dem.tif --crism zenodo_5575824/jezeroFinal.tif --geo data/s2_jezero.tif --geo-scored --rock zenodo_4931348/Jezero_Thermal_Inertia_v1.tiff --out grid.js --clip-km 5 --cell-px 8 --antenna-h 15`
4. 장비 무게.
   - 완료: 공구, 시료통, PLSS 질량을 아폴로 문서값으로 채움(`data/equipment.json`, Allton 1989 JSC-23454, NASA ALSJ).
   - 남음: 수트 질량(아폴로 A7L, NASA xEMU)은 수록하지 않음.
5. 방사선 장소 보정식: 현재는 근사식임(방향은 RAD 실측과 일치). 필요하면 천정각 의존(초기 메모에는 Guo 2023 으로 적혀 있음. `docs/2_sources.md` §8 의 해당 문헌은 Khaksarighiri 2023)으로 정교화함. 고도 보정 `altF` 는 설계 문서에만 있고 데모에는 없음.
6. 다중 소모품 복귀 한계: 설계와 용량 데이터(`data/consumables.json`)까지만 있고 데모에는 산소 기준 복귀선만 구현됨.

## 3. 하지 않는 것

- 생명점수 가중치의 데이터화: 가중치는 측정할 수 있는 양이 아니라 지표의 중요도임. 순위를 문헌으로 정하고 ROC 공식으로 계산하는 현재 방식을 유지함.
- 교신 음영 정밀화(전파 세기, 중계 위성): 참고용 레이어라 필수가 아님. 초기 문서에는 EVA 범위에서 영향이 2% 수준이라는 기록이 있으나 계산 근거가 저장소에 없어 다시 확인하지 못함.
