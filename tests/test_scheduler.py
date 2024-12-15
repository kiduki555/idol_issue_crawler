import unittest
from src.scheduler.task_scheduler import TaskScheduler
from src.db.mongo_client import MongoDBClient
from src.config.settings import Settings

class TestScheduler(unittest.TestCase):
    def setUp(self):
        settings = Settings(
            mongodb_uri="mongodb://localhost:27017",
            mongodb_name="test_db",
            dcinside_interval=1,
            fm_korea_interval=1,
            x_interval=1,
            reddit_interval=1
        )
        self.db_client = MongoDBClient(uri=settings.mongodb_uri, db_name=settings.mongodb_name)
        self.scheduler = TaskScheduler(self.db_client, settings)

    def tearDown(self):
        self.scheduler.stop()
        self.db_client.client.drop_database("test_db")

    def test_task_registration(self):
        self.scheduler.register_tasks()
        jobs = self.scheduler.scheduler.get_jobs()
        self.assertTrue(len(jobs) > 0, "Tasks should be registered in the scheduler.")

    def test_task_execution(self):
        self.scheduler.register_tasks()
        self.scheduler.start()
        jobs = self.scheduler.scheduler.get_jobs()
        self.assertTrue(len(jobs) > 0, "Scheduler should start and contain tasks.")

if __name__ == "__main__":
    unittest.main()
