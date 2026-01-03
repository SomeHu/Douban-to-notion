import requests
import time
import re
import json
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

# ---------------------------
# 通用工具
# ---------------------------

def clean_title(text: str) -> str:
    text = text.strip()
    text = text.split("\n")[0]
    text = text.split("/")[0]
    text = text.replace("[可播放]", "")
    return text.strip()


def extract_douban_id(url: str) -> str | None:
    m = re.search(r"/subject/(\d+)/", url)
    return m.group(1) if m else None


def extract_chinese_name(name: str) -> str | None:
    parts = re.findall(r"[\u4e00-\u9fff]+", name)
    if not parts:
        return None
    return "".join(parts)


# ---------------------------
# 详情页（公共信息）
# ---------------------------

def fetch_detail(url: str):
    resp = requests.get(url, headers=HEADERS, timeout=10)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    directors = []
    actors = []
    genres = []
    release_date = None
    douban_rating = None

    ld_json = soup.find("script", type="application/ld+json")
    if ld_json:
        try:
            data = json.loads(ld_json.string)

            # 🎬 导演
            raw_director = data.get("director")
            if isinstance(raw_director, dict):
                name = extract_chinese_name(raw_director.get("name", ""))
                if name:
                    directors.append(name)
            elif isinstance(raw_director, list):
                for d in raw_director:
                    name = extract_chinese_name(d.get("name", ""))
                    if name:
                        directors.append(name)

            # 🎭 主演（只中文）
            for a in data.get("actor", []):
                cn = extract_chinese_name(a.get("name", ""))
                if cn:
                    actors.append(cn)

            # 🎞 类型
            genres = data.get("genre", []) or []

            # 📅 上映日期
            release_date = data.get("datePublished")

            # ⭐ 豆瓣评分
            if "aggregateRating" in data:
                douban_rating = float(
                    data["aggregateRating"]["ratingValue"]
                )

        except Exception as e:
            print("⚠️ JSON-LD 解析失败:", e)

    return {
        "director": list(dict.fromkeys(directors)),
        "actors": list(dict.fromkeys(actors))[:5],
        "genres": genres,
        "release_date": release_date,
        "douban_rating": douban_rating,
    }


# ---------------------------
# 用户全部影视（含评分日期）
# ---------------------------

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

                # ⭐ 评分日期（只在“看过”里有）
                rating_date = None
                if status == "collect":
                    date_el = item.select_one(".date")
                    if date_el:
                        rating_date = date_el.text.strip()

                detail = fetch_detail(detail_url)

                yield {
                    "douban_id": douban_id,
                    "title": title,
                    "status": "看过" if status == "collect" else "想看",
                    "rating_date": rating_date,
                    **detail
                }

                time.sleep(1)

            start += 15
            time.sleep(2)
