"""생체 데이터셋 다운로드 가능 여부 확인.
실행:  pip install requests  →  python check_datasets.py
"""
import requests

DATASETS = [
    ("PhysioNet 트레드밀 (심박·VO2·속도) ⭐", "https://physionet.org/content/treadmill-exercise-cardioresp/1.0.1/", "열림 · 무료 · 로그인 불필요"),
    ("PhysioNet 자전거 GET (심박·VO2·파워)",   "https://physionet.org/content/actes-cycloergometer-exercise/1.0.0/", "열림 · 무료"),
    ("PhysioNet BUT CGM (ECG·활동·CPET)",      "https://physionet.org/content/but-cgm/1.0.0/", "열림 · 무료"),
    ("Kaggle 칼로리 소모 예측",                "https://www.kaggle.com/datasets", "계정 + Kaggle API 필요"),
    ("AI Hub 운동/생체신호 (한국)",            "https://aihub.or.kr", "로그인 필요 · 수동 다운"),
]

print("=== 데이터셋 접근 확인 ===\n")
for name, url, note in DATASETS:
    try:
        r = requests.head(url, timeout=25, allow_redirects=True)
        mark = "✅" if r.status_code < 400 else "⚠️"
        print(f"{mark} [{r.status_code}] {name}\n    {note}\n    {url}\n")
    except Exception as e:
        print(f"❌ {name} — 접속 실패: {e}\n")
print("→ PhysioNet 3개는 바로 받아져요(무료). Kaggle·AI Hub는 계정/로그인 필요.")
