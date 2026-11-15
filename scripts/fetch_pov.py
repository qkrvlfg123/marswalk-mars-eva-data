"""Perseverance 델타 전선 '풍경' 사진 수집 → pov_candidates.json
- Mastcam-Z / Navcam(풍경) 위주, SuperCam 망원샷 제외
- 델타 전선 시절 sol 범위로 필터 (조정 가능)
실행:  python fetch_pov.py
"""
import requests, json

SOL_MIN, SOL_MAX = 400, 700                      # Jezero 델타 전선 campaign (조정 가능)
CAMERAS = {"MCZ_LEFT", "MCZ_RIGHT", "NAVCAM_LEFT", "NAVCAM_RIGHT"}  # 풍경용

url = ("https://mars.nasa.gov/rss/api/?feed=raw_images&category=mars2020"
       "&feedtype=json&num=300&order=sol+asc"
       f"&condition_2={SOL_MIN}:sol:gte&condition_3={SOL_MAX}:sol:lte")

r = requests.get(url, timeout=60)
imgs = r.json().get("images", [])

out, seen = [], set()
for im in imgs:
    sol = im.get("sol") or 0
    if not (SOL_MIN <= sol <= SOL_MAX):          # API가 무시해도 파이썬서 한번 더
        continue
    cam = (im.get("camera") or {}).get("instrument", "")
    if cam not in CAMERAS:
        continue
    files = im.get("image_files") or {}
    pic = files.get("large") or files.get("full_res")
    key = (im.get("imageid") or "")[:28]
    if not pic or key in seen:
        continue
    seen.add(key)
    out.append({"sol": sol, "camera": cam,
                "date": im.get("date_taken_utc"), "img": pic})

json.dump(out, open("pov_candidates.json", "w"), ensure_ascii=False, indent=2)
print(f"{len(out)}개 (풍경, sol {SOL_MIN}~{SOL_MAX}) → pov_candidates.json")
if not out:
    print("※ 0개면: sol 범위를 바꿔보거나(예: 100~400), "
          "condition 필터가 안 먹는 것일 수 있어요 — 알려주세요.")
