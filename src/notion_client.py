from notion_client import Client


class NotionClient:
    def __init__(self, token, database_id):
        self.client = Client(auth=token)
        self.database_id = database_id

    def create_movie(self, movie):
        print("🧾 写入 Notion：", movie["title"])

        properties = {
            "标题": {
                "title": [
                    {"text": {"content": movie["title"]}}
                ]
            },
            "状态": {
                "select": {"name": movie["status"]}
            }
        }

        if movie.get("douban_rating") is not None:
            properties["豆瓣评分"] = {
                "number": movie["douban_rating"]
            }

        if movie.get("my_rating") is not None:
            properties["我的评分"] = {
                "number": movie["my_rating"]
            }

        if movie.get("rating_date"):
            properties["评分日期"] = {
                "date": {"start": movie["rating_date"]}
            }

        self.client.pages.create(
            parent={"database_id": self.database_id},
            properties=properties
        )
