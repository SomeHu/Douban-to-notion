from src.douban_fetch import fetch_all_movies
from src.notion_client import NotionClient
import os


def main():
    douban_user = os.environ["DOUBAN_USER_ID"]
    notion = NotionClient(
        os.environ["NOTION_TOKEN"],
        os.environ["NOTION_DATABASE_ID"]
    )

    movies = fetch_all_movies(douban_user)
    print(f"Total movies: {len(movies)}")

    for movie in movies:
        notion.create_movie(movie)


if __name__ == "__main__":
    main()
