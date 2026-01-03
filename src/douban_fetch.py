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
        url = f"https://movie.douban.com/people/{douban_user}/{status}?start={page*15}"
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")
        items = soup.select(".item")

        if not items:
            break

        for item in items:
            title = item.select_one(".title")
            link = item.select_one("a")

            if not title or not link:
                continue

            m = re.search(r"/subject/(\\d+)/", link["href"])
            douban_id = m.group(1) if m else ""

            movies.append({
                "title": " ".join(title.stripped_strings),
                "douban_id": douban_id,
                "url": link["href"],
                "status": status
            })

        page += 1
        time.sleep(1)

    return
