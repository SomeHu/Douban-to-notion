import requests
import time
from bs4 import BeautifulSoup


HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def clean_title(raw):
    return raw.split("/")[0].strip()


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

            resp = requests.get(
                url,
                headers=HEADERS,
                params=params,
                timeout=10
            )
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
                title_raw = item.select_one(".title")
                title = clean_title(title_raw.text) if title_raw else "未知标题"

                rating_el = item.select_one(".rating_nums")
                douban_rating = float(rating_el.text) if rating_el else None

                my_rating_el = item.select_one(".rating")
                my_rating = None
                if my_rating_el:
                    cls = my_rating_el.get("class", [])
                    for c in cls:
                        if c.startswith("rating"):
                            try:
                                my_rating = int(c.replace("rating", "")) / 10
                            except:
                                pass

                date_el = item.select_one(".date")
                rating_date = date_el.text if date_el else None

                yield {
                    "title": title,
                    "status": "看过" if status == "collect" else "想看",
                    "douban_rating": douban_rating,
                    "my_rating": my_rating,
                    "rating_date": rating_date,
                }

            start += 15
            time.sleep(2)
