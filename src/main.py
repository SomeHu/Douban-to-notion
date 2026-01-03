import os
from src.douban_fetch import fetch_all_movies
from src.notion_client import NotionClient


def main():
    douban_user = os.getenv("DOUBAN_USER")
    if not douban_user:
        raise ValueError("❌ 缺少环境变量 DOUBAN_USER")

    notion = NotionClient()

    print("🚀 开始同步（去重 + 强制更新）")

    for movie in fetch_all_movies(douban_user):
        notion.upsert_movie(movie)

    print("✅ 同步完成")


if __name__ == "__main__":
    main()
