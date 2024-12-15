from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from src.crawlers.dcinside_crawler import DCInsideCrawler
from src.crawlers.fm_korea_crawler import FMKoreaCrawler
from src.crawlers.reddit_crawler import RedditCrawler
from src.crawlers.x_crawler import XCrawler
from src.db.mongo_client import MongoDBClient
from src.config.settings import Settings

class TaskScheduler:
    def __init__(self, db_client, settings):
        self.scheduler = BackgroundScheduler()
        self.db_client = db_client
        self.settings = settings

    def register_tasks(self):
        """
        Register all scheduled tasks.
        """
        # DCInside Crawler
        self.scheduler.add_job(
            self.run_dcinside_crawler,
            IntervalTrigger(minutes=self.settings.dcinside_interval),
            id="dcinside_crawler",
            replace_existing=True,
        )

        # FM Korea Crawler
        self.scheduler.add_job(
            self.run_fm_korea_crawler,
            IntervalTrigger(minutes=self.settings.fm_korea_interval),
            id="fm_korea_crawler",
            replace_existing=True,
        )

        # X Crawler
        self.scheduler.add_job(
            self.run_x_crawler,
            IntervalTrigger(minutes=self.settings.x_interval),
            id="x_crawler",
            replace_existing=True,
        )

        # Reddit Crawler
        self.scheduler.add_job(
            self.run_reddit_crawler,
            IntervalTrigger(minutes=self.settings.reddit_interval),
            id="reddit_crawler",
            replace_existing=True,
        )

    def run_dcinside_crawler(self):
        crawler = DCInsideCrawler(self.db_client)
        crawler.fetch_posts(gallery_id=self.settings.dcinside_gallery_id, max_pages=3)

    def run_fm_korea_crawler(self):
        crawler = FMKoreaCrawler(self.db_client)
        crawler.fetch_posts(board_id=self.settings.fm_korea_board_id, max_pages=3)

    def run_x_crawler(self):
        crawler = XCrawler(
            self.db_client,
            api_key=self.settings.x_api_key,
            api_secret=self.settings.x_api_secret,
            access_token=self.settings.x_access_token,
            access_secret=self.settings.x_access_secret,
        )
        crawler.fetch_tweets(query=self.settings.x_query, count=10)

    def run_reddit_crawler(self):
        crawler = RedditCrawler(
            self.db_client,
            client_id=self.settings.reddit_client_id,
            client_secret=self.settings.reddit_client_secret,
            user_agent=self.settings.reddit_user_agent,
        )
        crawler.fetch_posts(subreddit_name=self.settings.reddit_subreddit, limit=10)

    def start(self):
        """
        Start the scheduler.
        """
        self.register_tasks()
        self.scheduler.start()
        print("Scheduler started...")

    def stop(self):
        """
        Stop the scheduler.
        """
        self.scheduler.shutdown()
        print("Scheduler stopped...")
