from notion_client import Client
from datetime import datetime


class NotionClient:
    def __init__(self, token, database_id):
        self.client = Client(auth=token)
        self.database_id = database_id

        self.status_map = {
            "collect": "看过",
            "wish": "想看",
            "do": "在看"
        }

    def create_movie(self, movie):
        properties = {
            "Name": {
                "title": [
                    {"text": {"content": movie["title"]}}
                ]
            },
            "Douban ID": {
                "rich_text": [
                    {"text": {"content": movie.get("douban_id", "")}}
                ]
            },
            "Douban Link": {
                "url": movie.get("url")
            },
            "Status": {
                "select": {
                    "name": self.status_map.get(movie["status"], "看过")
                }
            },
            "Sync Time": {
                "date": {
                    "start": datetime.utcnow().isoformat()
                }
            }
        }

        if movie.get("douban_rating") is not None:
            properties["Douban Rating"] = {
                "number": movie["douban_rating"]
            }

        if movie.get("director"):
            properties["Director"] = {
                "rich_text": [
                    {"text": {"content": movie["director"]}}
                ]
            }

        if movie.get("release_date"):
            properties["Release Date"] = {
                "date": {
                    "start": movie["release_date"]
                }
            }

        if movie.get("genres"):
            properties["Genres"] = {
                "multi_select": [
                    {"name": g} for g in movie["genres"]
                ]
            }

        if movie.get("my_rating") is not None:
            properties["My Rating"] = {
                "number": movie["my_rating"]
            }

        if movie.get("rating_date"):
            properties["Rating Date"] = {
                "date": {
                    "start": movie["rating_date"]
                }
            }

        self.client.pages.create(
            parent={"database_id": self.database_id},
            properties=properties
        )
