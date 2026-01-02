import os
from src.douban_fetch import fetch_collect_movies
from src.notion_client import NotionClient


if __name__ == "__main__":
    douban_user = os.getenv("DOUBAN_USER_ID")
    notion_token = os.getenv("NOTION_TOKEN")
    database_id = os.getenv("NOTION_DATABASE_ID")

    movies = fetch_collect_movies(douban_user, page_limit=1)

    notion = NotionClient(notion_token, database_id)

    for m in movies:
        notion.create_movie(m)
