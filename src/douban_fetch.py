import requests
import time
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def clean_title(text: str) -> str:
    text = text.strip()
    text = text.split("\n")[0]
    text = text.split("/")[0]
    text = text.replace("[可播放]", "")
    return text.strip()


def parse_my_rating(item):
    """
    支持：
    - rating45 class
    - ★★★★☆ 文本
    """
    rating_el = item.select_one(".rating")
    if not rating_el:
        return None

    # 情况 1：class rating45
    for cls in rating_el.get("class", []):
        if cls.startswith("rating"):
            try:
                return int(cls.replace("rating", "")) / 10
            except:
                pass

    # 情况 2：星星文本
    stars = rating_el.text.strip()
    if stars:
        return stars.count("★")

    return None


def fetch_detail(url: str):
    resp = requests.get(url, headers=HEADERS, timeout=10)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    director = None
    director_el = soup.select_one("#info span a")
    if director_el:
        director = director_el.text.strip()

    genres = [g.text for g in soup.select("#info span[property='v:genre']")]

    release_date = None
    date_el = soup.select_one("span[property='v:initialReleaseDate']")
    if date_el:
        release_date = date_el.text.split("(")[0]

    douban_rating = None
    rating_el = soup.select_one("strong[property='v:average']")
    if rating_el and rating_el.text.strip():
        try:
            douban_rating = float(rating_el.text)
        except:
            pass

    return {
        "director": director,
        "genres": genres,
        "release_date": release_date,
        "douban_rating": douban_rating,
    }


def fetch_all_movies(douban_user):
    statuses = ["collect", "wish"]

    for status in statuses:
        start = 0
        empty_pages = 0

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
                empty_pages += 1
                if empty_pages >= 2:
                    break
            else:
                empty_pages = 0

            for item in items:
                link_el = item.select_one(".info a")
                raw_title = link_el.text if link_el else "未知标题"
                title = clean_title(raw_title)

                detail_url = link_el["href"] if link_el else None

                my_rating = parse_my_rating(item)

                date_el = item.select_one(".date")
                rating_date = date_el.text.strip() if date_el else None

                detail = fetch_detail(detail_url) if detail_url else {}

                yield {
                    "title": title,
                    "status": "看过" if status == "collect" else "想看",
                    "my_rating": my_rating,
                    "rating_date": rating_date,
                    **detail
                }

                time.sleep(1)

            start += 15
            time.sleep(2)
