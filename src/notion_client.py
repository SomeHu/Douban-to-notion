from notion_client import Client


class NotionClient:
    def __init__(self, token, database_id):
        self.client = Client(auth=token)
        self.database_id = database_id

    def find_by_douban_id(self, douban_id: str):
        resp = self.client.databases.query(
            database_id=self.database_id,
            filter={
                "property": "douban_id",
                "rich_text": {"equals": douban_id}
            }
        )
        results = resp.get("results", [])
        return results[0]["id"] if results else None

    def build_props(self, movie: dict):
        props = {
            "标题": {
                "title": [{"text": {"content": movie["title"]}}]
            },
            "状态": {
                "select": {"name": movie["status"]}
            },
            "douban_id": {
                "rich_text": [{"text": {"content": movie["douban_id"]}}]
            }
        }

        if movie.get("douban_rating") is not None:
            props["豆瓣评分"] = {"number": movie["douban_rating"]}

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

        return props

    def upsert_movie(self, movie: dict):
        page_id = self.find_by_douban_id(movie["douban_id"])
        props = self.build_props(movie)

        if page_id:
            print("🔁 更新：", movie["title"])
            self.client.pages.update(
                page_id=page_id,
                properties=props
            )
        else:
            print("🆕 新建：", movie["title"])
            self.client.pages.create(
                parent={"database_id": self.database_id},
                icon={
                    "type": "emoji",
                    "emoji": "📺"
                },
                properties=props
            )
