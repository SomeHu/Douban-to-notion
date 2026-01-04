from notion_client import Client
import os

class NotionClient:
    def __init__(self):
        self.client = Client(auth=os.environ["NOTION_TOKEN"])
        self.database_id = os.environ["NOTION_DATABASE_ID"]
        self.page_map = {}  # douban_id -> page_id

    # --------------------------------
    # 启动时：一次性加载数据库
    # --------------------------------
    def preload_pages(self):
        print("📥 预加载 Notion 数据库索引")
        cursor = None

        while True:
            resp = self.client.search(
                filter={"property": "object", "value": "page"},
                start_cursor=cursor
            )

            for page in resp.get("results", []):
                parent = page.get("parent", {})
                if parent.get("database_id") != self.database_id:
                    continue

                props = page.get("properties", {})
                douban_prop = props.get("豆瓣ID")
                if not douban_prop:
                    continue

                texts = douban_prop.get("rich_text", [])
                if not texts:
                    continue

                douban_id = texts[0]["text"]["content"]
                self.page_map[douban_id] = page["id"]

            if not resp.get("has_more"):
                break
            cursor = resp.get("next_cursor")

        print(f"✅ 已加载 {len(self.page_map)} 条 Notion 页面")

    # --------------------------------
    # 构建属性
    # --------------------------------
    def build_properties(self, movie):
        props = {
            "名称": {
                "title": [{"text": {"content": movie["title"]}}]
            },
            "豆瓣ID": {
                "rich_text": [{"text": {"content": movie["douban_id"]}}]
            },
            "状态": {
                "select": {"name": movie["status"]}
            }
        }

        if movie.get("douban_rating") is not None:
            props["豆瓣评分"] = {"number": movie["douban_rating"]}

        if movie.get("release_date"):
            props["上映日期"] = {"date": {"start": movie["release_date"]}}

        if movie.get("rating_date"):
            props["评分日期"] = {"date": {"start": movie["rating_date"]}}

        if movie.get("director"):
            props["导演"] = {
                "multi_select": [{"name": d} for d in movie["director"]]
            }

        if movie.get("actors"):
            props["主演"] = {
                "multi_select": [{"name": a} for a in movie["actors"]]
            }

        if movie.get("genres"):
            props["类型"] = {
                "multi_select": [{"name": g} for g in movie["genres"]]
            }

        return props

    # --------------------------------
    # 真·upsert（不可能重复）
    # --------------------------------
    def upsert_movie(self, movie):
        douban_id = movie["douban_id"]
        props = self.build_properties(movie)

        if douban_id in self.page_map:
            self.client.pages.update(
                page_id=self.page_map[douban_id],
                properties=props,
                icon={"emoji": "📺"}
            )
        else:
            page = self.client.pages.create(
                parent={"database_id": self.database_id},
                properties=props,
                icon={"emoji": "📺"}
            )
            self.page_map[douban_id] = page["id"]
