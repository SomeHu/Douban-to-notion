import os
from src.douban_fetch import fetch_all_movies
from src.notion_client import NotionClient


def main():
    douban_user = os.getenv("DOUBAN_USER")
    notion_token = os.getenv("NOTION_TOKEN")
    notion_database_id = os.getenv("NOTION_DATABASE_ID")

    print("DEBUG DOUBAN_USER =", repr(douban_user))

    if not douban_user:
        raise ValueError("❌ 缺少环境变量 DOUBAN_USER")

    notion = NotionClient(
        token=notion_token,
        database_id=notion_database_id
    )

    success = 0
    failed = 0

    print("🚀 开始同步豆瓣数据")

    for idx, movie in enumerate(fetch_all_movies(douban_user), start=1):
        print(f"➡️ [{idx}] 写入 Notion：{movie.get('title')}")

        try:
            notion.create_movie(movie)
            success += 1
        except Exception as e:
            failed += 1
            print("❌ 写入失败", e)

    print("====== 完成 ======")
    print("成功：", success)
    print("失败：", failed)


if __name__ == "__main__":
    main()
