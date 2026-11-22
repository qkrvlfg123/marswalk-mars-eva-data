"""MARSWALK 심박 — 실측 보정 + 합성 EVA 데이터 생성.
① PhysioNet 트레드밀 실측(속도·심박·VO2)으로 '심박↔%VO2' 곡선을 보정
② 보정 곡선 + Pandolf(화성 보정)로 EVA 시나리오 합성 데이터 생성

출력은 `data/synthetic_eva.json` 형식을 그대로 따름:
  {"_source":…, "_model":…, "_sustainable_def":…, "scenario":[{t_min, slope_deg,
   load_kg, pctVO2, HR_bpm, O2_Lmin, sustainable}, …]}

사용:
  pip install pandas numpy
  # 1) 데이터 다운 (둘 중 하나)
  #    AWS :  aws s3 sync --no-sign-request s3://physionet-open/treadmill-exercise-cardioresp/ ./physionet_data/
  #    wget:  wget -r -N -c -np -nH --cut-dirs=3 https://physionet.org/files/treadmill-exercise-cardioresp/1.0.1/ -P ./physionet_data/
  # 2) 실행 (repo 어디서 실행해도 같은 경로에 씀)
  python scripts/calibrate_hr.py [physionet_data_디렉터리]
"""
import glob, os, sys, json
import numpy as np, pandas as pd

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_PATH = os.path.join(REPO, "data", "synthetic_eva.json")

def resolve_data_dir():
    """physionet_data 위치 — 인자 > 현재 디렉터리 > repo 루트 순으로 찾음."""
    cands = ([sys.argv[1]] if len(sys.argv) > 1 else []) + [
        "physionet_data", os.path.join(REPO, "physionet_data")]
    for c in cands:
        if os.path.isdir(c): return c
    return cands[0]

def find_col(cols, *keys):
    for c in cols:
        if any(k in c.lower() for k in keys): return c
    return None

def load_physionet(data_dir):
    files = glob.glob(os.path.join(data_dir, "**", "*.csv"), recursive=True)
    if not files:
        print(f"데이터 없음({data_dir}). 먼저 다운로드:")
        print("  aws s3 sync --no-sign-request s3://physionet-open/treadmill-exercise-cardioresp/ ./physionet_data/")
        return None
    rows = []
    for f in files:
        try: df = pd.read_csv(f)
        except Exception: continue
        hr, vo2 = find_col(df.columns,"hr","heart"), find_col(df.columns,"vo2")
        if not hr or not vo2: continue
        d = df[[hr,vo2]].apply(pd.to_numeric, errors="coerce").dropna()
        d = d[(d[vo2]>0) & (d[hr]>40) & (d[hr]<220)]
        if len(d) < 10: continue
        vo2max = d[vo2].quantile(0.95)                 # 개인 최대 근사
        rows.append(pd.DataFrame({"pctVO2": d[vo2]/vo2max, "HR": d[hr]}))
    if not rows:
        print("HR/VO2 컬럼 못 찾음 — 파일 구조 확인"); return None
    print(f"[로드] 테스트 {len(rows)}건, 샘플 {sum(len(r) for r in rows)}개")
    return pd.concat(rows, ignore_index=True), len(rows)

def calibrate(df):
    """1차 회귀로 HR = intercept + slope·%VO2 보정, R² 동반 산출."""
    d = df[(df.pctVO2>0.1) & (df.pctVO2<=1.2)]
    slope, intercept = np.polyfit(d.pctVO2, d.HR, 1)
    pred = intercept + slope*d.pctVO2
    ss_res = float(((d.HR - pred)**2).sum())
    ss_tot = float(((d.HR - d.HR.mean())**2).sum())
    r2 = 1 - ss_res/ss_tot
    print(f"[보정] HR = {intercept:.1f} + {slope:.1f}·%VO2   (실측 {len(d)}샘플, R2={r2:.2f})")
    print(f"  → 안정심박 ≈ {intercept:.0f} bpm, 최대 증가분 ≈ {slope:.0f} bpm")
    print(f"  (기존 데모값: 70 + 116·%VO2 — 실측과 비교해 교체)")
    return float(intercept), float(slope), float(r2), int(len(d))

# ── Pandolf (화성) — %VO2는 화성 중력 반영, 심박곡선은 보편 ──
M, ETA, GMARS = 80, 2.0, 0.38
VO2ABS = 37.5*M/1000     # 3.0 L/min (VO2peak 37.5 ml/kg/min · ISS 남성 평균)
AGE = 34                 # NASA 후보 평균
HRMAX = 220 - AGE        # 186 bpm — 보정식 외삽을 이 값에서 끊음
AEROBIC_CAP = 1.0        # sustainable 플래그 기준 = %VO2 1.0(VO2peak 도달) 초과 여부.
                         # 체력(W') 모델의 지속가능 임계 0.35와는 다른 기준임.
pandolf = lambda L,v,G: 1.5*M + 2*(M+L)*(L/M)**2 + ETA*(M+L)*(1.5*v*v + 0.35*v*G*GMARS)

def generate(intercept, slope, r2, n_tests, n_samples):
    plan = [(0,5,20),(10,12,20),(20,15,25),(30,5,25),(40,8,20),(50,2,15)]  # (분,경사°,무게kg)
    scenario=[]
    for t,sl,load in plan:
        G=np.tan(np.radians(sl))*100
        MW=pandolf(load,1.0,G); o2=MW/348; pct=o2/VO2ABS
        HR=min(intercept+slope*pct, HRMAX)
        scenario.append({"t_min":t,"slope_deg":sl,"load_kg":load,
                         "pctVO2":round(pct,2),"HR_bpm":round(HR),
                         "O2_Lmin":round(o2,2),"sustainable":bool(pct<=AEROBIC_CAP)})
        print(f"  t={t:>2}분 경사{sl:>2}° 하중{load}kg → 대사율 {MW:.0f}W · "
              f"%VO2 {pct:.2f} · HR {round(HR)} bpm · O2 {o2:.2f} L/min"
              f"{'' if pct<=AEROBIC_CAP else '  (지속 불가)'}")
    doc = {
        "_source": f"PhysioNet treadmill ({n_tests}건 검사, {n_samples:,}샘플) 실측 보정",
        "_model": f"HR = {intercept:.1f} + {slope:.1f}*pctVO2 (R2={r2:.2f}), HRmax cap {HRMAX}",
        "_sustainable_def": f"pctVO2 <= {AEROBIC_CAP} (VO2peak 도달 여부). "
                            f"체력(W') 모델의 지속가능 임계 0.35와는 다른 기준",
        "scenario": scenario,
    }
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=2)
    print(f"\n[합성] {len(scenario)}스텝 → {os.path.relpath(OUT_PATH, os.getcwd())} (실측 보정 기반 EVA 시계열)")

if __name__=="__main__":
    loaded = load_physionet(resolve_data_dir())
    if loaded is not None:
        df, n_tests = loaded
        a, b, r2, n = calibrate(df)
        generate(a, b, r2, n_tests, n)
