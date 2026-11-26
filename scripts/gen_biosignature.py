#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
생명점수(biosignature) 가중치 생성기.
가중치 숫자는 직접 고르지 않음.
  1) 지표 5개의 순위(rank)만 과학 프레임워크 근거로 정함 (iMOST / Hartz&George / Mars2020 SDT).
  2) 순위 -> 숫자는 공개된 MCDA 공식으로 계산함.
     - ROC (Rank Order Centroid, Barron 1992): w_i = (1/N) * sum_{k=i..N} (1/k)
     - RS  (Rank Sum, Stillwell 1981):        w_i = (N+1-i) / sum_{j=1..N}(N+1-j)
출처: Barron & Barrett (1996) Management Science 42(11):1515-1523.

실행: python scripts/gen_biosignature.py   (어디서 실행해도 <repo>/data/weights.json 에 씀)
"""
import json, os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_PATH = os.path.join(REPO, "data", "weights.json")

def roc_weights(n):
    w = []
    for i in range(1, n + 1):
        w.append(sum(1.0 / k for k in range(i, n + 1)) / n)
    return w

def rs_weights(n):
    denom = sum(n + 1 - j for j in range(1, n + 1))  # = n(n+1)/2
    return [(n + 1 - i) / denom for i in range(1, n + 1)]

def r3(x):  # round to 3 dp
    return round(x, 3)

# ---- 지표 5개: 순위 = 과학 근거, 숫자 = 공식 ----
# rank 1 = 가장 중요 (보존 잠재력 + 신뢰도 최고)
indicators = [
    {
        "key": "S1", "rank": 1, "name": "함수/점토광물(필로실리케이트)",
        "layer": "CRISM 함수광물",
        "why": "점토는 유기물 보존 1순위 매질. iMOST가 보존 유리 퇴적물로 명시(인산염·탄산염·황산염·점토). Jezero 델타서 K-Al 점토가 수십억년 유기물 보존 확인.",
        "src": "iMOST(Des Marais 2018, NTRS 20180003291) · McMahon 2018 · Hickman-Lewis 2025(Nat.Commun 10.1038/s41467-025-57727-4)"
    },
    {
        "key": "S2", "rank": 2, "name": "퇴적·델타 맥락(세립 호성/삼각주)",
        "layer": "지질단위 SIM3464 + DEM 지형",
        "why": "세립 퇴적물(이암·델타)은 유기탄소 매장·보존에 유리. Gale 이암서 스멕타이트+유기물 검출.",
        "src": "Broz 2020(Life 10.3390/life10070113) · Gale mudstone(SAM)"
    },
    {
        "key": "S4", "rank": 3, "name": "물 활동 흔적(수성 맥락)",
        "layer": "CRISM 수화신호 + 수로/델타 지형",
        "why": "과거 액체물은 거주가능성의 전제. 수로·수화광물은 서식/보존 환경의 1차 지표.",
        "src": "iMOST 수성 맥락 · MSR SSTM 거주가능성 축"
    },
    {
        "key": "S3", "rank": 4, "name": "보존성 염류(황산염·탄산염·염화물)",
        "layer": "THEMIS/CRISM 염류·증발광물",
        "why": "황산염·탄산염은 iMOST 보존 유리 광물. 증발염은 물 증거이자 유기물 포집 가능. 단독 신뢰도는 점토보다 낮음.",
        "src": "iMOST(Des Marais 2018) · THEMIS chloride(Osterloo 2008)"
    },
    {
        "key": "S5", "rank": 5, "name": "로버 현장 근접(in-situ 검증)",
        "layer": "Perseverance/MSL 확인 노두",
        "why": "직접검출은 신뢰도 최고(현장서 Sᵢ=4). 단 로버가 간 곳 근처만 커버(공간범위 좁음) → 가중치는 낮게, 있으면 보너스.",
        "src": "Mars2020 raw(mars.nasa.gov) · PDS · CoLD scale(Green 2021 Nature)"
    },
]

N = len(indicators)
roc = roc_weights(N)
rs = rs_weights(N)
assert abs(sum(roc) - 1) < 1e-9 and abs(sum(rs) - 1) < 1e-9

# rank 순서대로 가중치 부여
for ind in indicators:
    ind["w_roc"] = r3(roc[ind["rank"] - 1])
    ind["w_rs"] = r3(rs[ind["rank"] - 1])

out = {
    "_what": "생명점수 = Σ wᵢ·Sᵢ. Sᵢ=지점별 0~4 증거강도(SSTM식), wᵢ=지표 중요도.",
    "_key_idea": "가중치 숫자는 손으로 고르지 않음. 지표 '순위'만 과학으로 정하고 공식이 숫자 계산.",
    "_rank_basis": "순위 근거 = iMOST 보존광물 우선순위 + Hartz&George(2022) 신뢰도/검출도 + Mars2020 SDT 생체신호 유형",
    "_weight_formula": {
        "ROC": "Rank Order Centroid: w_i=(1/N)·Σ_{k=i..N}(1/k) — 상위 강조. Barron 1992.",
        "RS": "Rank Sum: w_i=(N+1-i)/ΣN — 완만. Stillwell 1981.",
        "src": "Barron & Barrett (1996) Management Science 42(11):1515-1523"
    },
    "_default": "w_roc (과학권장). 기존 데모값 0.30/0.25/0.20/0.15/0.10 ≈ RS와 거의 동일 → RS도 정당.",
    "_score_scale": "Sᵢ 0~4: 0 없음 / 1 약한 간접 / 2 궤도 암시 / 3 강한 궤도·분광 / 4 로버 현장 확인 (SSTM·CoLD식 단계)",
    "_normalize": "cell_raw=Σwᵢ·Sᵢ(0~4) → 0~100 = cell_raw/4·100",
    "_safety_note": "이 점수는 '어디가 과학적으로 좋은가'만. 안전(복귀선·경사·피폭)은 별도 게이트가 결정. recommend = safety_gate × science_score. 최종 go/no-go = 우주인.",
    "indicators": indicators,
    "presets_rank": {
        "과학권장(기본)": {"order": ["S1", "S2", "S4", "S3", "S5"], "weights": "ROC"},
        "물추적": {"order": ["S4", "S1", "S2", "S3", "S5"], "weights": "ROC"},
        "검증우선": {"order": ["S5", "S1", "S2", "S4", "S3"], "weights": "RS"}
    }
}

with open(OUT_PATH, "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)

print("ROC:", [r3(x) for x in roc], "sum", round(sum(roc), 4))
print("RS :", [r3(x) for x in rs], "sum", round(sum(rs), 4))
print("written data/weights.json")
