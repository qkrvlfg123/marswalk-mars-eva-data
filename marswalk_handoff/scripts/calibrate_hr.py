"""MARSWALK 심박 — 실측 보정 + 합성 EVA 데이터 생성.
① PhysioNet 트레드밀 실측(속도·심박·VO2)으로 '심박↔%VO2' 곡선을 보정
② 보정 곡선 + Pandolf(화성 보정)로 EVA 시나리오 합성 데이터 생성

사용:
  pip install pandas numpy
  # 1) 데이터 다운 (둘 중 하나)
  #    AWS :  aws s3 sync --no-sign-request s3://physionet-open/treadmill-exercise-cardioresp/ ./physionet_data/
  #    wget:  wget -r -N -c -np -nH --cut-dirs=3 https://physionet.org/files/treadmill-exercise-cardioresp/1.0.1/ -P ./physionet_data/
  # 2) 실행
  python calibrate_hr.py
"""
import glob, os, json
import numpy as np, pandas as pd

DATA_DIR = "physionet_data"

def find_col(cols, *keys):
    for c in cols:
        if any(k in c.lower() for k in keys): return c
    return None

def load_physionet():
    files = glob.glob(os.path.join(DATA_DIR, "**", "*.csv"), recursive=True)
    if not files:
        print("데이터 없음. 먼저 다운로드:")
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
    return pd.concat(rows, ignore_index=True)

def calibrate(df):
    d = df[(df.pctVO2>0.1) & (df.pctVO2<=1.2)]
    slope, intercept = np.polyfit(d.pctVO2, d.HR, 1)
    print(f"[보정] HR = {intercept:.1f} + {slope:.1f}·%VO2   (실측 {len(d)}샘플)")
    print(f"  → 안정심박 ≈ {intercept:.0f} bpm, 최대 증가분 ≈ {slope:.0f} bpm")
    print(f"  (기존 데모값: 70 + 116·%VO2 — 실측과 비교해 교체)")
    return float(intercept), float(slope)

# ── Pandolf (화성) — %VO2는 화성 중력 반영, 심박곡선은 보편 ──
M, ETA, GMARS = 80, 2.0, 0.38
VO2ABS = 37.5*M/1000     # 3.0 L/min
pandolf = lambda L,v,G: 1.5*M + 2*(M+L)*(L/M)**2 + ETA*(M+L)*(1.5*v*v + 0.35*v*G*GMARS)

def generate(intercept, slope):
    plan = [(0,5,20),(10,12,20),(20,18,25),(30,5,25),(40,8,20),(50,2,15)]  # (분,경사°,무게kg)
    out=[]
    for t,sl,load in plan:
        G=np.tan(np.radians(sl))*100
        MW=pandolf(load,1.0,G); o2=MW/348; pct=o2/VO2ABS
        HR=intercept+slope*pct
        out.append({"t_min":t,"slope_deg":sl,"load_kg":load,"MW_watt":round(MW),
                    "pctVO2":round(pct,2),"HR_bpm":round(HR),"O2_rate_Lmin":round(o2,2)})
    json.dump(out, open("synthetic_eva.json","w"), ensure_ascii=False, indent=2)
    print(f"\n[합성] {len(out)}스텝 → synthetic_eva.json (실측 보정 기반 EVA 시계열)")

if __name__=="__main__":
    df=load_physionet()
    if df is not None:
        a,b=calibrate(df); generate(a,b)
