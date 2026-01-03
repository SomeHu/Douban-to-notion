import os
from src.douban_fetch import fetch_all_movies
from src.notion_client import NotionClient


def main():
    # ===== 基础配置 =====
    douban_user = os.getenv("DOUBAN_USER")
    notion_token = os.getenv("NOTION_TOKEN")
    notion_database_id = os.getenv("NOTION_DATABASE_ID")

    if not douban_user:
        raise ValueError("❌ 缺少环境变量 DOUBAN_USER")
    if not notion_token:
        raise ValueError("❌ 缺少环境变量 NOTION_TOKEN")
    if not notion_database_id:
        raise ValueError("❌ 缺少环境变量 NOTION_DATABASE_ID")

    # ===== 初始化 Notion 客户端 =====
    notion = NotionClient(
        token=notion_token,
        database_id=notion_database_id
    )

    print("🚀 开始从豆瓣抓取并同步到 Notion")

    success = 0
    failed = 0

    # ===== 核心：边抓边写 =====
    for idx, movie in enumerate(fetch_all_movies(douban_user), start=1):
        title = movie.get("title", "未知标题")
        print(f"➡️ [{idx}] 正在写入 Notion：{title}")

        try:
            notion.create_movie(movie)
            success += 1
        except Exception as e:
            failed += 1
            print(f"❌ 写入失败：{title}")
            print(e)

    print("====== 同步完成 ======")
    print(f"✅ 成功写入：{success}")
    print(f"⚠️ 写入失败：{failed}")


if __name__ == "__main__":
    main()
