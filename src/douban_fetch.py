import requests
from bs4 import BeautifulSoup
import re
import time

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def clean_title(raw_title: str) -> str:
    title = raw_title.replace("[可播放]", "").strip()
    title = title.split("/")[0].strip()
    title = re.sub(r"（.*?）", "", title)
    return title.strip()


def fetch_detail_info(subject_url):
    """
    从详情页提取：
    - 豆瓣评分
    - 导演
    - 上映日期
    - 类型
    """
    info = {
        "douban_rating": None,
        "director": None,
        "release_date": None,
        "genres": []
    }

    try:
        resp = requests.get(subject_url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        # 豆瓣平均评分
        rating_el = soup.select_one("strong[property='v:average']")
        if rating_el and rating_el.text.strip():
            info["douban_rating"] = float(rating_el.text.strip())

        # 导演
        director_el = soup.select_one("a[rel='v:directedBy']")
        if director_el:
            info["director"] = director_el.text.strip()

        # 上映日期（取第一个）
        date_el = soup.select_one("span[property='v:initialReleaseDate']")
        if date_el:
            info["release_date"] = date_el.text.strip()

        # 类型（可能有多个）
        genre_els = soup.select("span[property='v:genre']")
        info["genres"] = [g.text.strip() for g in genre_els if g.text.strip()]

    except Exception:
        pass

    return info


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

            raw_title = " ".join(title_el.stripped_strings)
            title = clean_title(raw_title)

            match = re.search(r"/subject/(\\d+)/", link_el["href"])
            douban_id = match.group(1) if match else ""

            # 抓详情页信息
            detail = fetch_detail_info(link_el["href"])
            time.sleep(0.5)

            # 我的评分 & 日期（仅看过）
            my_rating = None
            rating_date = None

            if status == "collect":
                rating_el = item.select_one(".rating")
                if rating_el:
                    for cls in rating_el.get("class", []):
                        if cls.startswith("rating"):
                            try:
                                my_rating = int(cls.replace("rating", "")) / 2
                            except Exception:
                                pass

                date_el = item.select_one(".date")
                if date_el:
                    rating_date = date_el.text.strip()

            movies.append({
                "title": title,
                "douban_id": douban_id,
                "url": link_el["href"],
                "status": status,
                "douban_rating": detail["douban_rating"],
                "director": detail["director"],
                "release_date": detail["release_date"],
                "genres": detail["genres"],
                "my_rating": my_rating,
                "rating_date": rating_date
            })

        page += 1
        time.sleep(1)

    return movies


def fetch_all_movies(douban_user):
    all_movies = []
    for status in ["collect", "wish", "do"]:
        all_movies.extend(fetch_movies_by_status(douban_user, status))
    return all_movies
