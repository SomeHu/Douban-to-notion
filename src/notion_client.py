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
        """
        movie = {
            title: str,
            douban_id: str,
            url: str,
            status: collect | wish | do
        }
        """

        title = movie["title"].replace("\n", " ").strip()

        properties = {
            "Name": {
                "title": [
                    {
                        "text": {
                            "content": title
                        }
                    }
                ]
            },
            "Douban ID": {
                "rich_text": [
                    {
                        "text": {
                            "content": movie.get("douban_id", "")
                        }
                    }
                ]
            },
            "Douban Link": {
                "url": movie.get("url", "")
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

        try:
            self.client.pages.create(
                parent={"database_id": self.database_id},
                properties=properties
            )
        except Exception as e:
            print(f"❌ Failed to create page: {title}")
            print(e)
