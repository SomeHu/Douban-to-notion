from src.douban_fetch import fetch_collect_movies
from src.notion_client import NotionClient
import os

def main():
    douban_user = os.environ["DOUBAN_USER_ID"]
    notion_token = os.environ["NOTION_TOKEN"]
    database_id = os.environ["NOTION_DATABASE_ID"]

    movies = fetch_collect_movies(douban_user, page_limit=1)
    print(f"Fetched {len(movies)} movies")

    notion = NotionClient(notion_token, database_id)

    for m in movies:
        notion.create_movie(m)
        print("Created:", m["title"])

if __name__ == "__main__":
    main()
