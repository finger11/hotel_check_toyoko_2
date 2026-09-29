import json
from datetime import datetime, timezone
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeoutError

START = "2026-11-07"
END = "2026-11-09"
KEYWORD = "객실 선택"

# name은 원하는 호텔 이름으로 바꾸세요 (이슈 제목에 사용됨)
HOTELS = [
    {"code": "00221", "name": "부산서면"},
    {"code": "00194", "name": "부산역"},
    {"code": "00178", "name": "부산중앙역"},
    {"code": "00256", "name": "부산해운대"},
]

def build_url(code):
    return (
        "https://www.toyoko-inn.com/korea/search/result/room_plan/"
        f"?hotel={code}&start={START}&end={END}&room=1&people=2&smoking=noSmoking"
    )

def check_hotel(context, hotel):
    url = build_url(hotel["code"])
    item = {
        "code": hotel["code"],
        "name": hotel["name"],
        "url": url,
        "ok": True,
        "found": False,
        "count": 0,
        "note": "",
    }
    page = context.new_page()
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=60000)
        try:
            page.wait_for_load_state("networkidle", timeout=60000)
        except PWTimeoutError:
            pass
        page.wait_for_selector("button", timeout=20000)

        count = page.locator("button", has_text=KEYWORD).count()
        item["count"] = count
        item["found"] = count > 0
    except Exception as e:
        item["ok"] = False
        item["note"] = str(e).replace("\n", " ")[:300]
    finally:
        page.close()
    return item

def main():
    now = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            locale="ko-KR",
            user_agent="Mozilla/5.0",
            viewport={"width": 1280, "height": 2000},
        )
        for hotel in HOTELS:
            results.append(check_hotel(context, hotel))
        browser.close()

    print(json.dumps({"checked_at": now, "hotels": results}, ensure_ascii=False))

if __name__ == "__main__":
    main()
