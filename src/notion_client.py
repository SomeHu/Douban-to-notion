import requests
from datetime import datetime

class NotionClient:
    def __init__(self, token, database_id):
        self.database_id = database_id
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json"
        }

    def create_movie(self, movie):
        url = "https://api.notion.com/v1/pages"

        payload = {
            "parent": {"database_id": self.database_id},
            "properties": {
                "Title": {
                    "title": [{"text": {"content": movie["title"]}}]
                },
                "Douban ID": {
                    "rich_text": [{"text": {"content": movie["douban_id"]}}]
                },
                "Year": {"number": int(movie["year"]) if movie["year"] else None},
                "Rating": {"number": float(movie["rating"]) if movie["rating"] else None},
                "My Rating": {"number": int(movie["my_rating"]) if movie["my_rating"] else None},
                "Douban Link": {"url": movie["link"]},
                "Last Sync": {
                    "date": {"start": datetime.utcnow().isoformat()}
                }
            }
        }

        res = requests.post(url, headers=self.headers, json=payload)
        res.raise_for_status()
