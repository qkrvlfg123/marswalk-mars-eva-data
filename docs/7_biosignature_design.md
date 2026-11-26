# MARSWALK 생명점수(Biosignature Score) 상세 설계 (갱신 2026-11-15)

> 목적지 선정에 쓰는 과학 점수의 설계 문서임. 지표 순위는 문헌 프레임워크로 정하고, 가중치 숫자는 공식으로 계산하며, 안전은 별도 게이트가 우선함.
> 점수 정의는 데이터(JSON)로 분리돼 있음: `data/weights.json`, `data/layers.json`.

---

## 구현 현황 (2026-11-15): S1, S2 실데이터 적용, score 커버리지 100%

| 지표 | 입력 레이어 | 상태 | 커버리지 |
|---|---|---|---|
| S1 함수/점토광물 | CRISM 광물맵 (Zenodo 5575824, Parente, Itoh, Saranathan) | 실데이터 투입 | 2,488 / 3,067칸 (81.1%) |
| S2 퇴적, 델타 맥락 | USGS 지질맵 SIM 3464 (Sun & Stack 2020) | 실데이터 투입 | 3,067 / 3,067칸 (100%) |
| S3 보존성 염류 | (Jezero 에 드묾) | 설계 완료, 미적용 | 해당 적음 |
| S4 물 활동 | (S1, S2 에 내재) | 설계 완료, 미적용 | 이미 반영 |
| S5 로버 현장 근접 | 없음 | 미투입 | 없음 |

> 번호 규약: 코드(`build_grid.py` 의 `ROC_DEFAULT`)와 가중치 기준으로 S4 가 물 활동(순위 3, ROC 0.157), S3 가 보존성 염류(순위 4, ROC 0.090)임. ROC 는 순위로 가중치가 정해지므로 번호와 순위가 다름.

- S4 물 활동, 설계 완료 미적용(이미 반영): S1(점토, 함수광물)과 S2(델타, 퇴적)가 모두 물로 형성, 퇴적된 지표임. 과거 액체 물 활동은 S1, S2 에 이미 들어 있어 별도 레이어를 더하면 같은 신호를 두 번 세게 됨. 루브릭과 가중치(순위 3, ROC 0.157)는 설계로 유지하고 Jezero 에는 투입하지 않음.
- S3 보존성 염류, 설계 완료 미적용(해당 적음): 황산염, 염화물 같은 보존성 염류는 iMOST 보존광물이지만 Jezero 는 염류가 드물어(주 신호가 점토, 탄산염, 델타 퇴적) 변별력이 낮음. 루브릭과 가중치(순위 4, ROC 0.090)는 설계로 유지하고 투입하지 않음.
- 생명점수는 S1, S2 실데이터로 전 칸(100%)을 채움. 격자 산출물은 `grid.js`, `grid.geojson` (칸 약 160m, 기지 5km 클립, 3,067칸).
- score 최소 / 평균 / 최대 = 25 / 42.7 / 100. 델타 팬과 점토가 겹치는 칸이 80~100 점대를 이룸.
- 점수는 투입된 지표만 재정규화함: `score = Σ(wᵢ·Sᵢ, 투입된 i) / Σ(wᵢ, 투입된 i) / 4 × 100`. 현재 분모는 w_S1 + w_S2 = 0.457 + 0.257 = 0.714. S3~S5 가 들어오면 다시 혼합됨. 없는 값은 채우지 않음.
- Jezero floor unit 의 S2 는 1 임(호저 저지). Perseverance 착륙 후 바닥이 화성암(Máaz, Séítah)으로 확인돼 퇴적 등급에서 낮춤. 델타 팬(Jezero fan 1, 2, Nili Planum fan)은 S2 4.
- 미투입으로 남은 지표는 S5(로버 근접)임. 안전 레이어(경사, 교신)는 DEM 실데이터로 반영돼 있음.

생성 명령(저장소 루트에서 실행):

```
python scripts/build_grid.py --dem jezero_dem.tif \
  --crism zenodo_5575824/jezeroFinal.tif \
  --geo data/s2_jezero.tif --geo-scored \
  --rock zenodo_4931348/Jezero_Thermal_Inertia_v1.tiff \
  --out grid.js --clip-km 5 --cell-px 8 --antenna-h 15
```

S2 래스터는 `scripts/make_s2.py` 가 SIM 3464 의 GeoUnits_v1 폴리곤을 유닛별 S2(0~4)로 바꿔 `data/s2_jezero.tif` 로 만듦.

---

## 0. 요약

1. 생명점수 = Σ wᵢ·Sᵢ. 지점마다 지표 5개(Sᵢ, 0~4)를 가중합함.
2. 가중치 wᵢ 는 직접 고르지 않음. 지표 순위만 문헌으로 정하고 공식(ROC, RS)이 숫자를 계산함. 숫자의 근거가 공식으로 남음.
3. 생명점수는 보조 지표임. 안전(복귀선, 경사, 피폭)이 별도 게이트로 추천을 잠금. 최종 판단은 우주인이 하고 안전이 우선함.

---

## 1. 점수 공식

```
생명점수(cell) = Σ wᵢ · Sᵢ(cell)      # i = S1..S5
0~100 환산      = (Σ wᵢ·Sᵢ) / 4 · 100   # Sᵢ 최대 4, Σwᵢ=1 → 최대 4
```

- Sᵢ: 지점별 증거 강도(0~4). 그 칸에서 지표가 얼마나 강하게 나타나는지를 뜻함.
- wᵢ: 지표 중요도(합 1). 그 지표가 일반적으로 얼마나 중요한지를 뜻함.
- 두 역할을 나눔. 로버 현장 확인은 신뢰도가 가장 높으므로 있으면 Sᵢ=4 로 반영하고, 커버리지가 좁으므로 가중치 wᵢ 는 낮게 둠.
- 실제 격자 계산은 구현 현황의 재정규화식을 씀. 지표가 하나도 없는 칸은 null 임.

### Sᵢ 0~4 척도 (SSTM, CoLD 방식 단계)

| 점수 | 뜻 |
|---|---|
| 0 | 신호 없음 |
| 1 | 약한 간접 정황 |
| 2 | 궤도 관측 암시 |
| 3 | 강한 궤도, 분광 신호 |
| 4 | 로버 현장 확인 |

근거: MSR SSTM(증거 추적 행렬), CoLD scale(Confidence of Life Detection, Green et al. 2021 *Nature*)의 증거 단계 개념.

구현된 S1, S2 루브릭은 궤도 자료만으로 4점을 줌(아래 채점 루브릭). 위 척도의 4점 정의(로버 현장 확인)와 다르며, 로버 확인 여부는 S5 로 따로 다루는 구조임.

---

## 2. 지표 5개와 순위의 근거

순위 기준은 iMOST 보존광물 우선순위, Hartz & George (2022) 신뢰도와 검출도, Mars 2020 SDT 생체신호 유형임.

| 순위 | 지표 | 입력 레이어 | 상태 | 순위 이유 | 근거 |
|---|---|---|---|---|---|
| 1 | 함수/점토광물 | CRISM 광물맵 (Zenodo 5575824) | 실데이터 투입 | 점토는 유기물 보존에 가장 유리한 매질임. iMOST 가 보존에 유리한 퇴적물로 명시함. Jezero 델타에서 수십억 년 보존이 확인됨 | iMOST (Des Marais 2018), McMahon 2018, Hickman-Lewis 2025 |
| 2 | 퇴적, 델타 맥락 | 지질 SIM 3464 (Sun & Stack 2020) | 실데이터 투입 | 세립 퇴적물(이암, 델타)은 유기탄소 매장과 보존에 유리함. Gale 이암에서 점토와 유기물이 함께 검출됨 | Broz 2020, Gale SAM |
| 3 | 물 활동 흔적 | (S1, S2 에 내재) | 설계 완료, 미적용 | 과거 액체 물은 거주가능성의 전제임. 다만 S1 점토와 S2 델타가 모두 물로 형성, 퇴적된 지표라 이미 반영돼 있음. 이중 계산을 피하려고 따로 넣지 않음 | iMOST 수성 맥락, MSR SSTM |
| 4 | 보존성 염류 | THEMIS, CRISM 염류 | 설계 완료, 미적용 | 황산염, 탄산염은 iMOST 보존광물이지만 Jezero 는 염류가 드물어 변별력이 낮음. 설계만 유지함 | iMOST, Osterloo 2008 |
| 5 | 로버 현장 근접 | Perseverance, MSL | 미투입 | 직접 검출은 신뢰도가 가장 높지만 커버 범위가 좁아 가산 요소로 둠 | Mars 2020, CoLD (Green 2021) |

### S1, S2 채점 루브릭 (구현된 부분)

S1: CRISM 광물 → S1(0~4). 범례의 최근접 색으로 분류하고 칸 범위 안의 최빈 광물을 씀. 검정(미식별)과 흰색(배경)은 제외함.

| S1 | 광물 (CRISM 범례) | 근거 |
|---|---|---|
| 4 | 탄산염, 점토(스멕타이트, 카올리나이트), 함수실리카 | iMOST 1순위 보존광물 |
| 3 | 올리빈 + 점토 혼합(기타 수화) | 점토 신호가 있으나 혼합 |
| 1 | 올리빈, 휘석(현무암질) | 수화 광물 아님 |

S2: SIM 3464 지질 유닛 → S2(0~4). 유닛 폴리곤을 래스터화하고 칸 범위 평균을 씀.

| S2 | 지질 유닛 | 근거 |
|---|---|---|
| 4 | Jezero fan 1, 2, Nili Planum fan (삼각주 퇴적) | Broz 2020: 세립 델타, 호성 퇴적물이 유기물 보존에 가장 유리 |
| 3 | Smooth unit, undivided (평활 퇴적평원) | 세립일 가능성 |
| 1 | Jezero floor (호저), etched, Nili Planum, 풍성 사구 | floor 는 화성암(Máaz, Séítah, Perseverance 실측)이라 퇴적이 아님 |
| 0 | Rugged bright, Crater rim, ejecta, interior | 충돌 기원, 노출암 |

문헌 링크 전체는 `docs/2_sources.md` §8 에 있음.

---

## 3. 가중치: 순위에서 숫자를 계산하는 방식

0.30, 0.25, 0.20 같은 숫자를 직접 고르면 그 숫자의 근거를 댈 수 없음. 그래서 지표의 순위만 문헌으로 정하고, 순위를 숫자로 바꾸는 일은 공개된 MCDA 공식에 맡김.

> 출처: Barron & Barrett (1996) *Management Science* 42(11):1515-1523. 사람에게서 정확한 가중치를 직접 얻는 것은 존재하지 않는 정밀도를 요구하는 일이므로, 순위만 받고 대리 가중치(surrogate weight)로 변환한다는 내용임.

### 두 공식

| 공식 | 식 | 특징 |
|---|---|---|
| ROC (Rank Order Centroid, Barron 1992) | wᵢ = (1/N)·Σ_{k=i..N}(1/k) | 상위 지표를 강하게 강조 |
| RS (Rank Sum, Stillwell 1981) | wᵢ = (N+1−i)/Σ | 완만하게 차등 |

### N=5 계산 결과 (합 1.0 확인)

| 순위 | ROC | RS |
|---|---|---|
| 1 | 0.457 | 0.333 |
| 2 | 0.257 | 0.267 |
| 3 | 0.157 | 0.200 |
| 4 | 0.090 | 0.133 |
| 5 | 0.040 | 0.067 |

- 기본은 ROC(과학권장)임. 상위 지표(점토)를 강조하는 점이 보존 과학의 우선순위와 맞음.
- 초기 데모값 0.30 / 0.25 / 0.20 / 0.15 / 0.10 은 RS 와 거의 같음. RS 도 대안으로 쓸 수 있음.
- 프리셋은 순위를 바꾸는 방식임(물추적, 검증우선). 슬라이더로 숫자를 조정하지 않고 순위를 재배열하면 공식이 다시 계산함.
- 계산은 `scripts/gen_biosignature.py` 가 하고 결과는 `data/weights.json` 에 있음.

---

## 4. 레이어에서 점수까지의 흐름

```
[과학 레이어]  CRISM, 지질, THEMIS, 로버
     │  각 칸에서 레이어값 → Sᵢ(0~4) 루브릭 채점
     ▼
  생명점수 = Σ wᵢ·Sᵢ  →  0~100  →  히트맵
     │
     ▼
[안전 레이어]  복귀선, 경사, 피폭, 통신  →  게이트
     │
     ▼
화면 추천 = 게이트 × 생명점수
```

- 전처리: Jezero CTX DEM 20m, CRISM, 지질, THEMIS 열관성을 공통 격자(칸 약 160m, 3,067칸)로 리샘플해 루트의 `grid.geojson` 으로 만듦. 칸 속성은 `slope_deg`, `comm`, `S1`~`S5`, `score`, `rock` 임. 피폭 속성은 격자에 없고 데모가 실행 중에 계산함.
- 레이어별 루브릭은 `data/layers.json` 에 있음.

---

## 5. 안전 게이트: 보조 도구, 안전 우선

생명점수는 과학적으로 가치가 높은 곳만 나타냄. 안전 여부는 별개의 판단이고 둘을 섞지 않음.

```
recommend(cell) =
    0 (잠금)                          if gate_hard(cell) 실패
    science_score × soft_penalty      otherwise

gate_hard = (복귀선 반경 안) AND (경사 ≤ 25°) AND (피폭예산 내)
```

- HARD 게이트는 하드 제약(잠금)임. 복귀선 밖, 급경사, 피폭 초과 칸은 생명점수가 100 이어도 추천하지 않음. 회색으로 표시하고 사유를 보여 주며 go 버튼을 비활성화함.
- SOFT 게이트는 감점이나 가중임. 경사와 토질은 체력 소모를 늘리고(Pandolf η=2.0), 통신 음영은 보수적으로 감점함.
- 복귀선이 가장 우선함. 소모품이 줄면 반경이 줄어, 앞서 추천되던 먼 고득점 지점이 잠김. 산소가 90% 여도 너무 멀면 잠기고, 20% 여도 가까우면 통과함.
- 데모 구현 범위: 경사 25° 초과 칸의 A* 통행 차단과 산소 기준 복귀선이 구현돼 있음. 피폭 예산 게이트와 soft_penalty 곱은 설계 단계임.

### 구조의 근거 (NASA 문헌)

NASA 가 개발 중인 PersEIDS(Personalized EVA Informatics and Decision Support)와 같은 방향의 구조임.

- PersEIDS 는 EVA 타임라인에 소모품 사용을 자동 투영하고, 실시간 확률적 안전 평가를 제공하며, 경로를 추천하는 의사결정 보조 시스템임. (NTRS 20230007488)
- 시스템은 추천과 경고(advisory)만 하고 실행 판단은 사람이 함. MARSWALK 도 같음.
- EVA 의사결정 지원 연구의 공통 결론: 도구가 계산을 맡아 운영자가 상위 판단에 집중하게 하고, 안전과 시간의 트레이드오프를 여러 경로에 대해 동시에 평가해 제시함. (SpaceCHI 2025, 10.4230/OASIcs.SpaceCHI.2025.25, Miller & Feigh, Georgia Tech)

### 권한 원칙 (앱에 적용할 규칙)

1. 앱은 보조 도구임. 추천, 경고, 점수만 제공하고 명령하지 않음.
2. 최종 go/no-go 는 우주인이 판단함. 모든 추천은 우주인이 수용하거나 기각할 수 있음.
3. 안전 게이트는 끌 수 없음. HARD 게이트 해제는 우주인의 명시적 수동 확인을 거쳐야 하고 자동으로 무시할 수 없음. 안전이 과학보다 항상 우선함.

---

## 6. 구현 체크리스트

- [ ] `data/weights.json` 을 읽어 지표, 순위, ROC/RS 를 로드. UI 는 순위 드래그로 재배열(숫자 직접 입력 아님).
- [x] 각 칸 Sᵢ 채점 → 생명점수 히트맵: S1, S2 실데이터로 구현(`scripts/build_grid.py`), 전 칸 score 채움.
- [ ] 안전 레이어는 점수에 합산하지 않음. 게이트로만 사용.
- [ ] 잠긴 칸: 회색 + 사유("복귀선 밖" 등) + go 비활성.
- [ ] 복귀선 반경은 소모품 모델(`docs/1_model_spec_handoff.md` §3, §10)과 실시간 연동.
- [x] `grid.geojson`, `grid.js` 전처리: DEM 경사 + CRISM(S1) + SIM 3464(S2) + THEMIS(rock). 완료. 남은 것은 S5 레이어 투입임(S4 물 활동, S3 염류는 설계 완료 미적용).

---

## 7. 근거 출처 (이 문서)

- iMOST: Des Marais et al. (2018) "Seeking the Signs of Life", NTRS 20180003291. https://ntrs.nasa.gov/api/citations/20180003291/downloads/20180003291.pdf
- Hartz & George (2022) "Quantitative Framework for Astrobiology Strategies and in situ Biogenic Assessments" *Front. Astron. Space Sci.* 9:769607. https://doi.org/10.3389/fspas.2022.769607
- ExoMars Biosignature Score: Torres, Sefton-Nash, Vago (2022) EPSC2022-912. https://doi.org/10.5194/epsc2022-912
- CoLD scale: Green et al. (2021) "Call for a framework for reporting evidence for life beyond Earth" *Nature* 598:575-579. https://doi.org/10.1038/s41586-021-03804-9
- 점토 보존: McMahon et al. (2018), Hickman-Lewis et al. (2025) *Nat. Commun.* 10.1038/s41467-025-57727-4, Broz (2020) *Life* 10.3390/life10070113
- S1 CRISM 광물맵: Parente, Itoh, Saranathan "Jezero crater mineral map", Zenodo 5575824. https://doi.org/10.5281/zenodo.5575824 (Icarus 2021 방법 논문: Itoh & Parente, Saranathan & Parente)
- S2 지질맵: Sun, V. Z. & Stack, K. M. (2020) "Geologic map of Jezero crater and the Nili Planum region, Mars", USGS SIM 3464. https://doi.org/10.3133/sim3464
- ROC/RS 가중치: Barron & Barrett (1996) *Management Science* 42(11):1515-1523, Barron (1992), Stillwell et al. (1981)
- 의사결정 보조 (PersEIDS): NASA NTRS 20230007488, Miller & Feigh (GT), SpaceCHI 2025 (10.4230/OASIcs.SpaceCHI.2025.25)
