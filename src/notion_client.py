from notion_client import Client


class NotionClient:
    def __init__(self, token, database_id):
        self.client = Client(auth=token)
        self.database_id = database_id

    def create_movie(self, movie):
        print("🧾 写入 Notion：", movie["title"])

        props = {
            "标题": {
                "title": [{"text": {"content": movie["title"]}}]
            },
            "状态": {
                "select": {"name": movie["status"]}
            }
        }

        if movie.get("douban_rating") is not None:
            props["豆瓣评分"] = {"number": movie["douban_rating"]}

        if movie.get("my_rating") is not None:
            props["我的评分"] = {"number": movie["my_rating"]}

        if movie.get("rating_date"):
            props["评分日期"] = {"date": {"start": movie["rating_date"]}}

        if movie.get("director"):
            props["导演"] = {
                "rich_text": [{"text": {"content": movie["director"]}}]
            }

        if movie.get("genres"):
            props["类型"] = {
                "multi_select": [{"name": g} for g in movie["genres"]]
            }

        if movie.get("release_date"):
            props["上映日期"] = {
                "date": {"start": movie["release_date"]}
            }

        self.client.pages.create(
            parent={"database_id": self.database_id},
            properties=props
        )
