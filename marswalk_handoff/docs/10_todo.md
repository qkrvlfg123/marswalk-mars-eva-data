# MARSWALK — 추후 할 일 (TODO)

> 2026-11-14 기준. 지금 핸드오프 키트로 발표는 방어 가능. 아래는 "더 조이거나 실제 개발" 단계.

## 🔴 필수 (개발 전환 시)
1. **앱 실제 구현** — React + Leaflet + Recharts + Zustand.
   - 모델(대사율·산소·복귀선·체력·심박·피폭·생명점수)은 **순수 함수**로 이식. 참조: `marswalk_demo.html`, `1_model_spec_handoff.md`.
   - 패드(계획) / HUD(현장) 양면 UI.
2. **grid.geojson 앱 연동** — Leaflet GeoJSON 레이어로 경사·교신 색칠.
   - 안전 게이트 적용: `slope_deg>25` 또는 복귀선 밖 → 잠금(회색), `comm=shadow` → 교신 경고(참고용).
   - 연동 예시: `8_grid_guide.md` §5.

## 🟡 데이터 더 조이기 (선택, 신뢰도↑)
3. **생명점수 칸 Sᵢ 채우기** — CRISM 함수광물 + 지질 래스터 받아서:
   `python build_grid.py --dem jezero_dem.tif --crism clay.tif --geo delta.tif --out grid.geojson --cell-px 25`
   - ⚠ Sᵢ 0~4 변환 루브릭을 **CRISM 실제 단위에 맞게 고정** (지금은 5~95퍼센타일 정규화 예시).
4. **장비 무게 🟨 → 논문값** — 아폴로 A7L+PLSS / NASA xEMU 질량으로 교체(대표값 탈피).
5. **방사선 장소보정 식** — 현재 근사(방향은 RAD 실측). 필요시 Guo 2023 천정각 의존으로 정교화.

## 🟢 발표 준비
6. **데모 영상** — `marswalk_demo.html` 시나리오(핀 선택→생명점수→복귀선 수축→귀환) 30초~1분 녹화.
7. **스토리 3축** — ① 왜 사람(로봇 한계) ② 안전 최우선·보조도구(PersEIDS식) ③ 데이터 검증(이 키트).
8. **검증현황 1장**(`9_verification_status.md`)으로 Q&A 방어.

## 참고 — 안 해도 되는 것 (정직성)
- **생명점수 가중치**: 데이터 못 구함이 아니라 측정 불가능한 '중요도'. ROC 공식이 답. 더 할 것 없음.
- **교신 음영 정밀화**(전파세기·중계위성): 참고용 레이어라 필수 아님. EVA 범위 2%로 비이슈 확인됨.
