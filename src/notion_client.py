from notion_client import Client


class NotionClient:
    def __init__(self, token, database_id):
        self.client = Client(auth=token)
        self.database_id = database_id

    def find_by_douban_id(self, douban_id: str):
        resp = self.client.search(
            query=douban_id,
            filter={"property": "object", "value": "page"}
        )

        for page in resp.get("results", []):
            parent = page.get("parent", {})
            if parent.get("database_id") != self.database_id:
                continue

            props = page.get("properties", {})
            douban_prop = props.get("douban_id")
            if not douban_prop:
                continue

            texts = douban_prop.get("rich_text", [])
            if texts and texts[0]["plain_text"] == douban_id:
                return page["id"]

        return None

    def build_props(self, movie: dict):
        props = {
            "标题": {
                "title": [
                    {"text": {"content": movie["title"]}}
                ]
            },
            "状态": {
                "select": {"name": movie["status"]}
            },
            "douban_id": {
                "rich_text": [
                    {"text": {"content": movie["douban_id"]}}
                ]
            }
        }

        if movie.get("douban_rating") is not None:
            props["豆瓣评分"] = {
                "number": movie["douban_rating"]
            }

        if movie.get("rating_date"):
            props["评分日期"] = {
                "date": {"start": movie["rating_date"]}
            }

        if movie.get("director"):
            props["导演"] = {
                "rich_text": [
                    {"text": {"content": movie["director"]}}
                ]
            }

        if movie.get("actors"):
            props["主演"] = {
                "multi_select": [
                    {"name": actor} for actor in movie["actors"]
                ]
            }

        if movie.get("genres"):
            props["类型"] = {
                "multi_select": [
                    {"name": g} for g in movie["genres"]
                ]
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
