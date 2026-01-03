import requests
from bs4 import BeautifulSoup
import time
import re

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
}

def fetch_collect_movies(user_id, page_limit=1):
    """
    拉取豆瓣「看过」电影
    page_limit 控制页数，1页≈15条
    """
    results = []

    for page in range(page_limit):
        start = page * 15
        url = f"https://movie.douban.com/people/{user_id}/collect?start={start}&sort=time&rating=all&filter=all&mode=grid"

        resp = requests.get(url, headers=HEADERS, timeout=10)
        if resp.status_code != 200:
            print("请求失败:", url)
            break

        soup = BeautifulSoup(resp.text, "lxml")
        items = soup.select(".grid-view .item")

        if not items:
            break

        for item in items:
            title = item.select_one(".title")
            title_text = title.text.strip() if title else "Unknown"

        link_tag = item.select_one("a")
        if not link_tag:
            continue
        
        link = link_tag.get("href", "")
        match = re.search(r"subject/(\d+)/", link)
        
        if not match:
            # 不是影视条目，直接跳过
            continue
        
        douban_id = match.group(1)

            year = None
            year_node = item.select_one(".intro")
            if year_node:
                match = re.search(r"(\\d{4})", year_node.text)
                if match:
                    year = match.group(1)

            rating = None
            rating_node = item.select_one(".rating_num")
            if rating_node:
                rating = rating_node.text.strip()

            my_rating = None
            star = item.select_one(".rating")
            if star and "rating" in star["class"][-1]:
                my_rating = star["class"][-1].replace("rating", "")

            results.append({
                "title": title_text,
                "year": year,
                "douban_id": douban_id,
                "rating": rating,
                "my_rating": my_rating,
                "link": link
            })

        time.sleep(1)  # 别手贱

    return results


if __name__ == "__main__":
    USER_ID = "你的豆瓣ID"  # 例如 xiaohu123
    movies = fetch_collect_movies(USER_ID, page_limit=1)

    for m in movies:
        print(
            f"{m['title']} ({m['year']}) | "
            f"豆瓣ID:{m['douban_id']} | "
            f"豆瓣评分:{m['rating']} | "
            f"我的评分:{m['my_rating']}"
        )
