# MARSWALK — 생명점수(Biosignature Score) 상세 설계 (업데이트 2026-11-15)

> ① "어디로 갈까"를 정하는 과학 점수. **지표 순위는 프레임워크 근거, 가중치 숫자는 공식 계산, 안전은 별도 게이트가 최우선.**
> 개발 핸드오프용. 로직은 전부 데이터(JSON)로 분리 — `data/weights.json`, `data/layers.json`.

---

## ★ 구현 현황 (2026-11-15) — S1·S2 실데이터 적용, 커버리지 100%

| 지표 | 입력 레이어(실데이터) | 상태 | 커버리지 |
|---|---|---|---|
| **S1** 함수/점토광물 | CRISM 광물맵 (Zenodo 5575824, Parente·Itoh·Saranathan) | ✅ 실데이터 | 2,488/3,067 칸 (81.1%) |
| **S2** 퇴적·델타 맥락 | USGS 지질맵 **SIM3464** (Sun & Stack 2020) | ✅ 실데이터 | 3,067/3,067 칸 (100%) |
| S3 보존성 염류 | (Jezero 희박) | 🟦 **설계완료·비적용** | 해당 적음 |
| S4 물 활동 | (S1·S2에 내재) | 🟦 **설계완료·비적용** | 이미 반영 |
| S5 로버 현장 근접 | — | ⬜ 미투입 | — |

> 번호 규약: 코드(`build_grid.py` ROC_DEFAULT)·가중치 기준 **S4 = 물 활동(순위 3, ROC 0.157), S3 = 보존성 염류(순위 4, ROC 0.090)**. (ROC는 순위로 가중치가 정해지므로 번호 ≠ 순위)

- **S4 물 활동 = 설계완료·비적용(이미 반영):** S1(점토·함수광물)과 S2(델타·퇴적)가 **모두 물로 형성·퇴적된 지표**다. 즉 '과거 액체물 활동'은 S1·S2 안에 이미 내재 — 별도 레이어를 더하면 같은 물 신호를 이중계산하게 됨. 그래서 루브릭·가중치(순위 3, ROC 0.157)는 **설계로 유지**하되 Jezero에는 **별도 투입하지 않음**.
- **S3 보존성 염류 = 설계완료·비적용(해당 적음):** 황산염·염화물 같은 보존성 염류는 iMOST 보존광물이지만 **Jezero는 염류가 희박**(주 신호가 점토·탄산염·델타 퇴적)해 변별력이 낮다. 루브릭·가중치(순위 4, ROC 0.090)는 **설계로 유지**하되 투입하지 않음.

- **생명점수 = S1+S2 실데이터 기반, 전 칸(100%) 채움.** 격자 산출물 `grid.js`(칸≈160m, 기지 5km 클립, 3,067칸).
- **score min/평균/max = 25 / 42.7 / 100.** 델타 팬+점토 칸이 80~100 고득점 봉우리를 형성.
- **점수 = '가용 지표만 재정규화'**: `score = Σ(wᵢ·Sᵢ, 투입된 i) / Σ(wᵢ, 투입된 i) / 4 × 100`. 지금은 분모 = w_S1+w_S2 = 0.457+0.257 = 0.714. S3~S5가 들어오면 자동으로 재혼합(가짜값 안 채움).
- **Jezero floor unit = S2 1** (호저 저지). Perseverance 착륙 후 바닥이 **화성암(Máaz/Séítah 화성암질)** 으로 확인돼 '퇴적'에서 하향. 델타 팬(Jezero fan 1·2, Nili Planum fan) = S2 4.
- **남은 '미투입'은 S5(로버 근접)뿐.** S4(물 활동)·S3(염류)는 **설계완료·비적용**(아래 참조). 안전 레이어(경사·교신)는 DEM 실데이터로 이미 반영.

생성 커맨드:
```
python build_grid.py --dem jezero_dem.tif \
  --crism zenodo_5575824/jezeroFinal.tif \
  --geo data/s2_jezero.tif --geo-scored \
  --out grid.js --clip-km 5 --cell-px 8 --antenna-h 15
```
(S2 래스터는 `make_s2.py`가 SIM3464 GeoUnits_v1 폴리곤 → 유닛별 S2(0~4) → `data/s2_jezero.tif` 로 생성)

---

## 0. 세 줄 요약

1. **생명점수 = Σ wᵢ·Sᵢ** — 지점마다 지표 5개(Sᵢ, 0~4)를 가중합.
2. **가중치 wᵢ는 손으로 안 고름.** 지표 "순위"만 과학으로 정하면 공식(ROC/RS)이 숫자를 계산. → "왜 0.30이야?" 방어됨.
3. **생명점수는 보조.** 안전(복귀선·경사·피폭)이 별도 게이트로 추천을 잠금. **최종 판단은 우주인, 안전 최우선.**

---

## 1. 점수 공식

```
생명점수(cell) = Σ wᵢ · Sᵢ(cell)      # i = S1..S5
0~100 환산      = (Σ wᵢ·Sᵢ) / 4 · 100   # Sᵢ 최대 4, Σwᵢ=1 → 최대 4
```

- **Sᵢ = 지점별 증거 강도 (0~4):** 그 셀에서 지표가 얼마나 강하게 나타나나.
- **wᵢ = 지표 중요도 (합=1):** 그 지표가 일반적으로 얼마나 중요한가.
- 역할 분리가 중요: "로버 현장 확인"은 **신뢰도 최고 → 있으면 Sᵢ=4**로 반영하고, 커버리지가 좁으니 **가중치 wᵢ는 낮게**. 모순 없음.

### Sᵢ 0~4 척도 (SSTM·CoLD식 단계)

| 점수 | 뜻 |
|---|---|
| 0 | 신호 없음 |
| 1 | 약한 간접 정황 |
| 2 | 궤도 관측 암시 |
| 3 | 강한 궤도·분광 신호 |
| 4 | 로버 현장 확인 |

근거: MSR SSTM(증거 추적 행렬) · CoLD scale(Confidence of Life Detection, Green et al. 2021 *Nature*)의 "증거 단계" 개념.

---

## 2. 지표 5개 — 순위의 과학 근거

순위 기준 = **iMOST 보존광물 우선순위** + **Hartz & George(2022) 신뢰도/검출도** + **Mars 2020 SDT 생체신호 유형**.

| 순위 | 지표 | 입력 레이어 | 상태 | 왜 이 순위 | 근거 |
|---|---|---|---|---|---|
| 1 | **함수/점토광물** | CRISM 광물맵 (Zenodo 5575824) | ✅ 실데이터 | 점토 = 유기물 보존 1순위 매질. iMOST가 보존유리 퇴적물로 명시. Jezero 델타서 수십억년 보존 확인 | iMOST(Des Marais 2018) · McMahon 2018 · Hickman-Lewis 2025 |
| 2 | **퇴적·델타 맥락** | 지질 SIM3464 (Sun & Stack 2020) | ✅ 실데이터 | 세립 퇴적물(이암·델타)은 유기탄소 매장·보존 유리. Gale 이암서 점토+유기물 | Broz 2020 · Gale SAM |
| 3 | **물 활동 흔적** | (S1·S2에 내재) | 🟦 설계완료·비적용 | 과거 액체물 = 거주가능성 전제. **단 S1 점토·S2 델타가 모두 물 형성·퇴적 지표라 이미 반영** → 이중계산 피하려 별도 미투입 | iMOST 수성맥락 · MSR SSTM |
| 4 | **보존성 염류** | THEMIS/CRISM 염류 | 🟦 설계완료·비적용 | 황산염·탄산염은 iMOST 보존광물이나 **Jezero는 염류 희박**해 변별력↓ → 설계만 유지, 미투입 | iMOST · Osterloo 2008 |
| 5 | **로버 현장 근접** | Perseverance/MSL | ⬜ 미투입 | 직접검출 신뢰도 최고지만 커버 좁음 → 보너스 | Mars2020 · CoLD(Green 2021) |

### S1·S2 채점 루브릭 (구현된 분)

**S1 — CRISM 광물 → S1(0~4)** (범례 최근접색 분류, 칸 footprint 최빈 광물; 검정=미식별·흰색=배경 제외)

| S1 | 광물(SIM/CRISM 범례) | 근거 |
|---|---|---|
| 4 | 탄산염·점토(스멕타이트·카올리나이트)·함수실리카 | iMOST 1순위 보존광물 |
| 3 | 올리빈+점토 혼합(기타 수화) | 점토 신호 있으나 혼합 |
| 1 | 올리빈·휘석(현무암질) | 수화 아님 |

**S2 — SIM3464 지질유닛 → S2(0~4)** (유닛 폴리곤 래스터화, 칸 footprint 평균)

| S2 | 지질 유닛 | 근거 |
|---|---|---|
| 4 | Jezero fan 1·2, Nili Planum fan (**삼각주 퇴적**) | Broz 2020: 세립 델타·호성 퇴적물이 유기물 보존 최상 |
| 3 | Smooth unit, undivided (평활 퇴적평원) | 세립 가능 |
| 1 | **Jezero floor** (호저)·etched·Nili Planum·풍성사구 | floor=화성암(Máaz/Séítah, Perseverance 실측) → 퇴적 아님 |
| 0 | Rugged bright·Crater rim/ejecta/interior | 충돌·노출암 |

전체 링크는 `docs/2_모델근거_출처.md` §8.

---

## 3. 가중치 — 숫자를 안 고르는 법 (핵심)

**문제:** 0.30·0.25·0.20… 을 내가 고르면 "왜 그 숫자?"에 못 버팀.
**해법:** 지표 **순위만** 과학으로 정하고, 순위→숫자는 **공개된 MCDA 공식**으로 계산.

> 출처: **Barron & Barrett (1996)** *Management Science* 42(11):1515-1523. "정확한 가중치를 사람 머리에서 뽑는 건 존재하지 않는 정밀도를 요구한다 → 순위만 받고 surrogate weight로 변환."

### 두 공식

| 공식 | 식 | 특징 |
|---|---|---|
| **ROC** (Rank Order Centroid, Barron 1992) | wᵢ = (1/N)·Σ_{k=i..N}(1/k) | 상위 지표 강하게 강조 |
| **RS** (Rank Sum, Stillwell 1981) | wᵢ = (N+1−i)/Σ | 완만하게 차등 |

### N=5 계산 결과 (합=1.0 검증됨)

| 순위 | ROC | RS |
|---|---|---|
| 1 | **0.457** | 0.333 |
| 2 | 0.257 | 0.267 |
| 3 | 0.157 | 0.200 |
| 4 | 0.090 | 0.133 |
| 5 | 0.040 | 0.067 |

- **기본 = ROC(과학권장).** 상위 지표(점토) 강조가 보존과학과 부합.
- 기존 데모값 0.30/0.25/0.20/0.15/0.10 ≈ **RS와 거의 동일** → RS도 정당한 대안.
- **프리셋 = 순위 바꾸기**(물추적/검증우선). 슬라이더로 숫자를 만지는 게 아니라 **순위를 재배열**하면 공식이 다시 계산.

→ 발표 방어: *"가중치는 제가 고른 숫자가 아니라, 과학 프레임워크로 지표 순위를 정하고 Barron ROC 공식으로 계산한 값입니다."*

---

## 4. 레이어 → 점수 파이프라인

```
[과학 레이어]  CRISM·지질·THEMIS·로버
     │  각 셀에서 레이어값 → Sᵢ(0~4) 루브릭 채점
     ▼
  생명점수 = Σ wᵢ·Sᵢ  →  0~100  →  히트맵
     │
     ▼
[안전 레이어]  복귀선·경사·피폭·통신  →  게이트
     │
     ▼
화면 추천 = 게이트 × 생명점수
```

- 전처리: Jezero DEM·CRISM·지질을 **공통 격자(예 100m)**로 리샘플 → `data/grid.geojson` (셀마다 slope·Sᵢ·rad 속성).
- 레이어별 루브릭은 `data/layers.json`에 수록.

---

## 5. 안전 게이트 — "보조도구·안전 최우선" (설계의 핵심)

**생명점수는 '과학적으로 좋은 곳'만 말한다. 안전하냐는 별개다.** 이 둘을 섞지 않는다.

```
recommend(cell) =
    0 (잠금)                          if gate_hard(cell) 실패
    science_score × soft_penalty      otherwise

gate_hard = (복귀선 반경 안) AND (경사 ≤ 25°) AND (피폭예산 내)
```

- **HARD 게이트 = 하드 제약(잠금).** 복귀선 밖·급경사·피폭초과 셀은 **생명점수가 100이어도** 추천 안 함 → 회색 + 사유 표시, go 버튼 비활성.
- **SOFT 게이트 = 감점/가중.** 경사·흙질은 체력 소모↑(Pandolf η=2.0), 통신음영은 보수적 감점.
- **복귀선이 왕.** 소모품이 줄면 반경이 수축 → 아까 추천되던 먼 고득점 지점이 자동으로 잠김. (산소 90%라도 너무 멀면 잠금, 20%라도 가까우면 통과 — 사용자가 말한 그 로직.)

### 왜 이 구조가 정답인가 (NASA 근거)

이건 NASA가 실제로 만드는 **PersEIDS**(Personalized EVA Informatics and Decision Support)와 같은 철학이다:
- PersEIDS = EVA 타임라인에 **소모품 사용을 자동 투영**하고, **실시간 확률적 안전평가**를 주며, **경로를 추천**하는 **의사결정 보조** 시스템. (NTRS 20230007488)
- 즉 시스템은 **추천·경고(advisory)**만 하고, 실행 판단은 사람이. MARSWALK도 동일.
- EVA DSS 연구 공통 결론: 도구는 계산을 떠안아 **운영자가 상위 판단에 집중**하게 하고, **안전·시간 트레이드오프를 여러 경로에 대해 동시 평가**해 제시. (SpaceCHI 2025, 10.4230/OASIcs.SpaceCHI.2025.25 · Miller & Feigh, Georgia Tech)

### 권한 원칙 (앱에 박을 규칙)

1. **앱은 보조.** 추천·경고·점수만 제공. 명령하지 않음.
2. **최종 go/no-go = 우주인.** 모든 추천은 우주인이 수용/기각 가능.
3. **안전 게이트는 끌 수 없음.** HARD 게이트 해제는 우주인의 **명시적 수동 확인**을 거쳐야(자동 무시 불가). 안전이 과학보다 항상 우선.

---

## 6. 개발 전달 체크리스트

- [ ] `data/weights.json` 읽어 지표·순위·ROC/RS 로드. UI는 **순위 드래그**로 재배열(숫자 직접입력 아님).
- [x] 각 셀 Sᵢ 채점 → 생명점수 히트맵 — **S1·S2 실데이터로 구현**(`build_grid.py`), 전 칸 score 채움.
- [ ] 안전 레이어는 **점수에 합산 금지.** 게이트로만 사용.
- [ ] 잠긴 셀: 회색 + 사유("복귀선 밖" 등) + go 비활성.
- [ ] 복귀선 반경은 소모품 모델(§4, 모델스펙)과 실시간 연동.
- [x] `grid.geojson`/`grid.js` 전처리: DEM slope + CRISM(S1) + SIM3464(S2). **완료.** (잔여: S5 레이어 투입; S4 물활동·S3 염류는 설계완료·비적용)

---

## 7. 근거 출처 (이 문서)

- **iMOST** — Des Marais et al. (2018) "Seeking the Signs of Life", NTRS 20180003291 — https://ntrs.nasa.gov/api/citations/20180003291/downloads/20180003291.pdf
- **Hartz & George (2022)** "Quantitative Framework for Astrobiology Strategies and in situ Biogenic Assessments" *Front. Astron. Space Sci.* 9:769607 — https://doi.org/10.3389/fspas.2022.769607
- **ExoMars Biosignature Score** — Torres, Sefton-Nash, Vago (2022) EPSC2022-912 — https://doi.org/10.5194/epsc2022-912
- **CoLD scale** — Green et al. (2021) "Call for a framework for reporting evidence for life beyond Earth" *Nature* 598:575-579 — https://doi.org/10.1038/s41586-021-03804-9
- **점토 보존** — McMahon et al. (2018) · Hickman-Lewis et al. (2025) *Nat. Commun.* 10.1038/s41467-025-57727-4 · Broz (2020) *Life* 10.3390/life10070113
- **S1 CRISM 광물맵** — Parente, Itoh, Saranathan "Jezero crater mineral map", Zenodo 5575824 — https://doi.org/10.5281/zenodo.5575824 (Icarus 2021 방법: Itoh & Parente; Saranathan & Parente)
- **S2 지질맵** — Sun, V. Z. & Stack, K. M. (2020) "Geologic map of Jezero crater and the Nili Planum region, Mars", USGS **SIM 3464** — https://doi.org/10.3133/sim3464
- **ROC/RS 가중치** — Barron & Barrett (1996) *Management Science* 42(11):1515-1523 · Barron (1992) · Stillwell et al. (1981)
- **의사결정 보조(PersEIDS)** — NASA NTRS 20230007488 · Miller & Feigh (GT) · SpaceCHI 2025 (10.4230/OASIcs.SpaceCHI.2025.25)
