import requests
from bs4 import BeautifulSoup
import re
import time

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def fetch_collect_movies(douban_user, page_limit=1):
    movies = []

    for page in range(page_limit):
        url = f"https://movie.douban.com/people/{douban_user}/collect?start={page*15}"
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")
        items = soup.select(".item")

        for item in items:
            title = item.select_one(".title")
            link = item.select_one("a")

            if not title or not link:
                continue

            m = re.search(r"/subject/(\\d+)/", link["href"])
            douban_id = m.group(1) if m else None

            movies.append({
                "title": title.text.strip(),
                "douban_id": douban_id,
                "url": link["href"]
            })

        time.sleep(1)

    return movies
