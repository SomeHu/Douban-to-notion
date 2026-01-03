import requests
from bs4 import BeautifulSoup
import re
import time

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def fetch_movies_by_status(douban_user, status):
    movies = []
    page = 0

    while True:
        url = f"https://movie.douban.com/people/{douban_user}/{status}?start={page * 15}"
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")
        items = soup.select(".item")

        if not items:
            break

        for item in items:
            title_el = item.select_one(".title")
            link_el = item.select_one("a")

            if not title_el or not link_el:
                continue

            title = " ".join(title_el.stripped_strings)

            match = re.search(r"/subject/(\\d+)/", link_el["href"])
            douban_id = match.group(1) if match else ""

            movies.append({
                "title": title,
                "douban_id": douban_id,
                "url": link_el["href"],
                "status": status
            })

        page += 1
        time.sleep(1)

    return movies


def fetch_all_movies(douban_user):
    all_movies = []
    for status in ["collect", "wish", "do"]:
        all_movies.extend(fetch_movies_by_status(douban_user, status))
    return all_movies
