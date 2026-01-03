import requests

class NotionClient:
    def __init__(self, token, database_id):
        self.database_id = database_id
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json"
        }

    def create_movie(self, movie):
        payload = {
            "parent": {"database_id": self.database_id},
            "properties": {
                "Name": {
                    "title": [
                        {"text": {"content": movie["title"]}}
                    ]
                },
                "Douban ID": {
                    "rich_text": [
                        {"text": {"content": movie["douban_id"] or ""}}
                    ]
                },
                "Douban Link": {
                    "url": movie["url"]
                }
            }
        }

        res = requests.post(
            "https://api.notion.com/v1/pages",
            headers=self.headers,
            json=payload,
            timeout=10
        )

        if res.status_code >= 400:
            print(res.text)
            res.raise_for_status()
