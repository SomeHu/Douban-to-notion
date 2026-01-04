import os
from src.douban_fetch import fetch_all_movies
from src.notion_client import NotionClient


def main():
    # -------- 环境变量检查 --------
    douban_user = os.getenv("DOUBAN_USER")
    if not douban_user:
        raise ValueError("❌ 缺少环境变量 DOUBAN_USER")

    if not os.getenv("NOTION_TOKEN"):
        raise ValueError("❌ 缺少环境变量 NOTION_TOKEN")

    if not os.getenv("NOTION_DATABASE_ID"):
        raise ValueError("❌ 缺少环境变量 NOTION_DATABASE_ID")

    # -------- 初始化 Notion --------
    notion = NotionClient()

    # 🔑 关键步骤：预加载 Notion 数据库，构建 douban_id → page_id 索引
    notion.preload_pages()

    print("🚀 开始同步豆瓣影视到 Notion（去重 + 强制更新）")

    count = 0
    for movie in fetch_all_movies(douban_user):
        if not movie.get("douban_id"):
            continue

        notion.upsert_movie(movie)
        count += 1

    print(f"✅ 同步完成，共处理 {count} 条影视记录")


if __name__ == "__main__":
    main()
