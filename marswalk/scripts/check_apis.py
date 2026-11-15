"""MARSWALK 외부 데이터 확인 — 하나씩 실제 호출해서 되는지 점검.
실행:  python check_apis.py     (requests 필요: pip install requests)
"""
import requests

NASA_KEY = "DEMO_KEY"   # ← api.nasa.gov에서 무료키 받으면 여기 교체

def check_donki():
    url = (f"https://api.nasa.gov/DONKI/notifications"
           f"?startDate=2024-05-10&endDate=2024-05-12&type=all&api_key={NASA_KEY}")
    r = requests.get(url, timeout=30)
    print(f"[DONKI 우주기상] status {r.status_code}")
    data = r.json()
    print(f"  반환 {len(data)}건")
    if data:
        print("  첫 항목 필드:", list(data[0].keys()))
        print("  messageType:", data[0].get("messageType"),
              "| 시각:", data[0].get("messageIssueTime"))
    return r.status_code == 200 and len(data) > 0

def check_perseverance():
    url = ("https://mars.nasa.gov/rss/api/"
           "?feed=raw_images&category=mars2020&feedtype=json&num=3")
    r = requests.get(url, timeout=30)
    print(f"[Perseverance POV] status {r.status_code}")
    data = r.json()
    imgs = data.get("images", [])
    print(f"  이미지 {len(imgs)}장 (total {data.get('total_images')})")
    if imgs:
        im = imgs[0]
        print("  첫 이미지 필드:", list(im.keys()))
        print("  sol:", im.get("sol"),
              "| camera:", (im.get("camera") or {}).get("instrument"))
        print("  image_files:", im.get("image_files"))
    return r.status_code == 200 and len(imgs) > 0

def check_tile():
    url = ("https://cartocdn-gusc.global.ssl.fastly.net/opmbuilder/api/v1/"
           "map/named/opm-mars-basemap-v0-2/all/3/4/3.png")
    r = requests.get(url, timeout=30)
    ct = r.headers.get("content-type", "")
    print(f"[OpenPlanetary 타일] status {r.status_code}, {len(r.content)} bytes, {ct}")
    return r.status_code == 200 and "image" in ct

if __name__ == "__main__":
    results = []
    for name, fn in [("DONKI", check_donki),
                     ("Perseverance", check_perseverance),
                     ("OpenPlanetary 타일", check_tile)]:
        try:
            results.append((name, fn()))
        except Exception as e:
            print(f"  [{name}] 오류: {e}")
            results.append((name, False))
        print()
    print("=== 결과 요약 ===")
    for n, ok in results:
        print(f"  {n}: {'✅ 작동' if ok else '❌ 실패/빈값'}")
