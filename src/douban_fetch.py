import requests
import time
import re
import json
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64)"
}


def clean_title(text: str) -> str:
    text = text.strip()
    text = text.split("\n")[0]
    text = text.split("/")[0]
    text = text.replace("[可播放]", "")
    return text.strip()


def extract_douban_id(url: str):
    m = re.search(r"/subject/(\d+)/", url)
    return m.group(1) if m else None


def fetch_detail(url: str):
    resp = requests.get(url, headers=HEADERS, timeout=10)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    director = None
    actors = []
    genres = []
    release_date = None
    douban_rating = None

    # ===== JSON-LD（最稳定的数据源）=====
    ld_json = soup.find("script", type="application/ld+json")
    if ld_json:
        try:
            data = json.loads(ld_json.string)
            director = (
                data.get("director", {}).get("name")
                if isinstance(data.get("director"), dict)
                else None
            )
            actors = [
                a.get("name") for a in data.get("actor", []) if "name" in a
            ]
            genres = data.get("genre", []) or []
            release_date = data.get("datePublished")
            douban_rating = (
                float(data["aggregateRating"]["ratingValue"])
                if "aggregateRating" in data
                else None
            )
        except Exception as e:
            print("⚠️ JSON-LD 解析失败:", e)

    return {
        "director": director,
        "actors": actors[:5],
        "genres": genres,
        "release_date": release_date,
        "douban_rating": douban_rating,
    }


def fetch_all_movies(douban_user):
    statuses = ["collect", "wish"]

    for status in statuses:
        start = 0

        while True:
            print(f"⏳ 抓取豆瓣 {status} start={start}")

            url = f"https://movie.douban.com/people/{douban_user}/{status}"
            params = {
                "start": start,
                "sort": "time",
                "rating": "all",
                "filter": "all",
                "mode": "grid"
            }

            resp = requests.get(url, headers=HEADERS, params=params, timeout=10)
            resp.raise_for_status()

            soup = BeautifulSoup(resp.text, "html.parser")
            items = soup.select(".item")

            if not items:
                break

            for item in items:
                link_el = item.select_one(".info a")
                if not link_el:
                    continue

                title = clean_title(link_el.text)
                detail_url = link_el["href"]
                douban_id = extract_douban_id(detail_url)

                # ⭐ 评分日期（可能没有）
                rating_date = None
                date_el = item.select_one(".date")
                if date_el:
                    rating_date = date_el.text.strip()

                detail = fetch_detail(detail_url)

                movie = {
                    "douban_id": douban_id,
                    "title": title,
                    "status": "看过" if status == "collect" else "想看",
                    "rating_date": rating_date,
                    **detail
                }

                print("🎬 解析结果:", {
                    "title": movie["title"],
                    "actors": movie["actors"],
                    "rating_date": movie["rating_date"]
                })

                yield movie

                time.sleep(1)

            start += 15
            time.sleep(2)
