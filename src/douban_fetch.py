import requests
import time
import re
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


def extract_douban_id(url: str) -> str | None:
    """
    https://movie.douban.com/subject/1292052/
    → 1292052
    """
    m = re.search(r"/subject/(\d+)/", url)
    return m.group(1) if m else None


def fetch_detail(url: str):
    resp = requests.get(url, headers=HEADERS, timeout=10)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    director = None
    director_el = soup.select_one("#info span a")
    if director_el:
        director = director_el.text.strip()

    genres = [g.text.strip() for g in soup.select("#info span[property='v:genre']")]

    release_date = None
    date_el = soup.select_one("span[property='v:initialReleaseDate']")
    if date_el:
        release_date = date_el.text.split("(")[0]

    douban_rating = None
    for sel in [
        "strong[property='v:average']",
        "strong.rating_num",
        "span.rating_num",
    ]:
        el = soup.select_one(sel)
        if el and el.text.strip():
            try:
                douban_rating = float(el.text.strip())
                break
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
                if not link_el:
                    continue

                title = clean_title(link_el.text)
                detail_url = link_el["href"]
                douban_id = extract_douban_id(detail_url)

                detail = fetch_detail(detail_url)

                yield {
                    "douban_id": douban_id,
                    "title": title,
                    "status": "看过" if status == "collect" else "想看",
                    **detail
                }

                time.sleep(1)

            start += 15
            time.sleep(2)
