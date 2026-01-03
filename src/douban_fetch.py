import os
import requests

NOTION_API = "https://api.notion.com/v1/pages"
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

def create_movie(movie):
    props = {
        "剧名": {
            "title": [
                {"text": {"content": movie["title"]}}
            ]
        },
        "豆瓣ID": {
            "rich_text": [
                {"text": {"content": movie["douban_id"]}}
            ]
        },
        "链接": {
            "url": movie["link"]
        }
    }

    if movie.get("year"):
        props["年份"] = {"number": int(movie["year"])}

    if movie.get("rating"):
        props["评分"] = {"number": float(movie["rating"])}

    if movie.get("my_rating"):
        props["我的评分"] = {"number": int(movie["my_rating"])}

    payload = {
        "parent": {"database_id": DATABASE_ID},
        "properties": props
    }

    res = requests.post(NOTION_API, headers=HEADERS, json=payload)

    if res.status_code != 200:
        print("❌ Notion Error:", res.text)

    res.raise_for_status()
