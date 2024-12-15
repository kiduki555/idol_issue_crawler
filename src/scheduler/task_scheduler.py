from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from src.crawlers.nate_crawler import NateCrawler
from src.crawlers.dcinside_crawler import DCInsideCrawler

class TaskScheduler:
    def __init__(self, db_client, settings):
        self.scheduler = BackgroundScheduler()
        self.db_client = db_client
        self.settings = settings

    def register_tasks(self):
        """
        Register tasks dynamically for each platform's keywords.
        """
        keywords = self.fetch_keywords()
        for platform, platform_keywords in keywords.items():
            if platform == "nate" and platform_keywords:
                self.scheduler.add_job(
                    self.run_nate_crawler,
                    # IntervalTrigger(minutes=self.settings.nate_interval),
                    args=[platform_keywords],
                    id=f"nate_crawler",
                    replace_existing=True
                )
            # elif platform == "dcinside" and platform_keywords:
            #     self.scheduler.add_job(
            #         self.run_dcinside_crawler,
            #         IntervalTrigger(minutes=self.settings.dcinside_interval),
            #         args=[platform_keywords],
            #         id=f"dcinside_crawler",
            #         replace_existing=True
            #     )
            # Add other platforms (FM Korea, Reddit, etc.) here as needed

        print("[Scheduler] All tasks have been registered.")

    def fetch_keywords(self):
        collection = self.db_client.db["keywords"]
        document = collection.find_one({})
        if not document:
            print("[Scheduler] No keywords found in MongoDB.")
            return {}
        return {key: value for key, value in document.items() if key != "_id"}

    def run_nate_crawler(self, keywords):
        print(f"[Scheduler] Running Nate Pann crawler for keywords: {keywords}")
        try:
            nate_crawler = NateCrawler(self.db_client)
            for keyword in keywords:
                nate_crawler.fetch_posts(keyword, start_page=1, end_page=2)
        except Exception as e:
            print(f"[Scheduler] Error in Nate Pann crawler: {e}")

    def run_dcinside_crawler(self, keywords):
        print(f"[Scheduler] Running DCInside crawler for keywords: {keywords}")
        try:
            dc_crawler = DCInsideCrawler(self.db_client)
            for keyword in keywords:
                dc_crawler.fetch_posts(gallery_id=keyword, max_pages=1)
        except Exception as e:
            print(f"[Scheduler] Error in DCInside crawler: {e}")

    def start(self):
        """
        Start the scheduler.
        """
        print("[Scheduler] Starting the scheduler...")
        self.register_tasks()
        self.scheduler.start()
        print("[Scheduler] Scheduler started successfully.")

    def stop(self):
        """
        Stop the scheduler.
        """
        print("[Scheduler] Stopping the scheduler...")
        self.scheduler.shutdown()
        print("[Scheduler] Scheduler stopped.")
