import os
from src.douban_fetch import fetch_all_movies
from src.notion_client import NotionClient


def main():
    douban_user = os.getenv("DOUBAN_USER")
    notion_token = os.getenv("NOTION_TOKEN")
    notion_database_id = os.getenv("NOTION_DATABASE_ID")

    if not douban_user:
        raise ValueError("缺少 DOUBAN_USER")

    notion = NotionClient(notion_token, notion_database_id)

    print("🚀 开始同步（去重 + 更新）")

    for movie in fetch_all_movies(douban_user):
        if not movie.get("douban_id"):
            continue
        notion.upsert_movie(movie)

    print("✅ 同步完成")


if __name__ == "__main__":
    main()
