import requests
from bs4 import BeautifulSoup
import time
import re

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
}

def fetch_collect_movies(user_id, page_limit=1):
    results = []

    for page in range(page_limit):
        start = page * 15
        url = (
            f"https://movie.douban.com/people/{user_id}/collect"
            f"?start={start}&sort=time&rating=all&filter=all&mode=grid"
        )

        resp = requests.get(url, headers=HEADERS, timeout=10)
        if resp.status_code != 200:
            break

        soup = BeautifulSoup(resp.text, "lxml")
        items = soup.select(".grid-view .item")
        if not items:
            break

        for item in items:
            title_node = item.select_one(".title")
            if not title_node:
                continue
            title_text = title_node.text.strip()

            link_tag = item.select_one("a")
            if not link_tag:
                continue
            link = link_tag.get("href", "")

            match = re.search(r"subject/(\d+)/", link)
            if not match:
                continue
            douban_id = match.group(1)

            year = None
            intro = item.select_one(".intro")
            if intro:
                year_match = re.search(r"(\d{4})", intro.text)
                if year_match:
                    year = year_match.group(1)

            rating = None
            rating_node = item.select_one(".rating_num")
            if rating_node:
                rating = rating_node.text.strip()

            my_rating = None
            star = item.select_one(".rating")
            if star:
                for cls in star.get("class", []):
                    if cls.startswith("rating"):
                        my_rating = cls.replace("rating", "")
                        break

            results.append({
                "title": title_text,
                "year": year,
                "douban_id": douban_id,
                "rating": rating,
                "my_rating": my_rating,
                "link": link
            })

        time.sleep(1)

    return results
