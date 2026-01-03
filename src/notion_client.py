from notion_client import Client
import os

class NotionClient:
    def __init__(self):
        self.client = Client(auth=os.environ["NOTION_TOKEN"])
        self.database_id = os.environ["NOTION_DATABASE_ID"]

    # -------------------------
    # 查找已有页面（按 douban_id）
    # -------------------------
    def find_by_douban_id(self, douban_id):
        resp = self.client.databases.query(
            database_id=self.database_id,
            filter={
                "property": "豆瓣ID",
                "rich_text": {
                    "equals": douban_id
                }
            }
        )
        if resp["results"]:
            return resp["results"][0]["id"]
        return None

    # -------------------------
    # 构建 Notion 属性（统一入口）
    # -------------------------
    def build_properties(self, movie):
        props = {
            "名称": {
                "title": [
                    {
                        "text": {
                            "content": movie["title"]
                        }
                    }
                ]
            },
            "豆瓣ID": {
                "rich_text": [
                    {
                        "text": {
                            "content": movie["douban_id"]
                        }
                    }
                ]
            },
            "状态": {
                "select": {
                    "name": movie["status"]
                }
            }
        }

        # ⭐ 豆瓣评分
        if movie.get("douban_rating") is not None:
            props["豆瓣评分"] = {
                "number": movie["douban_rating"]
            }

        # 📅 上映日期
        if movie.get("release_date"):
            props["上映日期"] = {
                "date": {
                    "start": movie["release_date"]
                }
            }

        # 📅 评分日期
        if movie.get("rating_date"):
            props["评分日期"] = {
                "date": {
                    "start": movie["rating_date"]
                }
            }

        # 🎬 导演（multi-select）
        if movie.get("director"):
            props["导演"] = {
                "multi_select": [
                    {"name": d} for d in movie["director"]
                ]
            }

        # 🎭 主演（multi-select）
        if movie.get("actors"):
            props["主演"] = {
                "multi_select": [
                    {"name": a} for a in movie["actors"]
                ]
            }

        # 🎞 类型（multi-select）
        if movie.get("genres"):
            props["类型"] = {
                "multi_select": [
                    {"name": g} for g in movie["genres"]
                ]
            }

        return props

    # -------------------------
    # 核心：强制 upsert（不留空白）
    # -------------------------
    def upsert_movie(self, movie):
        page_id = self.find_by_douban_id(movie["douban_id"])
        props = self.build_properties(movie)

        if page_id:
            # 🔁 更新已有页面（字段级覆盖）
            self.client.pages.update(
                page_id=page_id,
                properties=props,
                icon={
                    "emoji": "📺"
                }
            )
        else:
            # 🆕 新建页面
            self.client.pages.create(
                parent={"database_id": self.database_id},
                properties=props,
                icon={
                    "emoji": "📺"
                }
            )
