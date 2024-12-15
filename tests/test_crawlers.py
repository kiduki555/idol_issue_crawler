import unittest
from src.crawlers.dcinside_crawler import DCInsideCrawler
from src.crawlers.fm_korea_crawler import FMKoreaCrawler
from src.crawlers.reddit_crawler import RedditCrawler
from src.crawlers.x_crawler import XCrawler
from src.db.mongo_client import MongoDBClient

class TestCrawlers(unittest.TestCase):
    def setUp(self):
        # 테스트용 MongoDB 설정
        self.db_client = MongoDBClient(uri="mongodb://localhost:27017", db_name="test_db")

    def tearDown(self):
        # 테스트 데이터베이스 정리
        self.db_client.client.drop_database("test_db")

    def test_dcinside_crawler(self):
        crawler = DCInsideCrawler(self.db_client)
        crawler.fetch_posts(gallery_id="example_gallery", max_pages=1)
        data = self.db_client.fetch_data("dcinside")
        self.assertTrue(len(data) > 0, "DCInsideCrawler should fetch data.")

    def test_fm_korea_crawler(self):
        crawler = FMKoreaCrawler(self.db_client)
        crawler.fetch_posts(board_id="example_board", max_pages=1)
        data = self.db_client.fetch_data("fmkorea")
        self.assertTrue(len(data) > 0, "FMKoreaCrawler should fetch data.")

    def test_reddit_crawler(self):
        crawler = RedditCrawler(
            self.db_client,
            client_id="dummy_client_id",
            client_secret="dummy_client_secret",
            user_agent="dummy_user_agent"
        )
        crawler.fetch_posts(subreddit_name="example_subreddit", limit=1)
        data = self.db_client.fetch_data("reddit")
        self.assertTrue(len(data) > 0, "RedditCrawler should fetch data.")

    def test_x_crawler(self):
        crawler = XCrawler(
            self.db_client,
            api_key="dummy_api_key",
            api_secret="dummy_api_secret",
            access_token="dummy_access_token",
            access_secret="dummy_access_secret"
        )
        crawler.fetch_tweets(query="example_query", count=1)
        data = self.db_client.fetch_data("x")
        self.assertTrue(len(data) > 0, "XCrawler should fetch data.")

if __name__ == "__main__":
    unittest.main()
