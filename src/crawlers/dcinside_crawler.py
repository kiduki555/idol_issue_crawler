from src.crawlers.base_crawler import BaseCrawler
from src.db.mongo_client import MongoDBClient
import re

class DCInsideCrawler(BaseCrawler):
    def __init__(self, db_client):
        super().__init__()
        self.db_client = db_client
        self.base_url = "https://gall.dcinside.com/board/lists/?id="

    def fetch_posts(self, gallery_id, max_pages=5):
        """
        Fetch posts from a DCInside gallery.
        """
        for page in range(1, max_pages + 1):
            url = f"{self.base_url}{gallery_id}&page={page}"
            html = self.get_html(url)
            if html:
                posts = self.parse_posts(html)
                self.store_posts(posts)

    def parse_posts(self, html):
        """
        Parse HTML to extract posts.
        """
        posts = []
        row_pattern = re.compile(r'<tr[^>]*>(.*?)</tr>', re.DOTALL)
        title_pattern = re.compile(r'<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>', re.DOTALL)
        for match in row_pattern.finditer(html):
            row_html = match.group(1)
            title_match = title_pattern.search(row_html)
            if not title_match:
                continue

            url = title_match.group(1)
            title = re.sub(r'<[^>]+>', '', title_match.group(2)).strip()
            posts.append({"title": title, "url": url, "source": "dcinside"})
        return posts

    def store_posts(self, posts):
        """
        Store parsed posts in MongoDB.
        """
        for post in posts:
            if self.db_client.insert_data("dcinside", post):
                print(f"Inserted: {post['title']}")
            else:
                print(f"Duplicate skipped: {post['title']}")
