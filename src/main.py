import os
from dotenv import load_dotenv
from src.scheduler.task_scheduler import TaskScheduler
from src.db.mongo_client import MongoDBClient
from src.config.settings import Settings

def main():
    # Load environment variables
    load_dotenv()

    # Load settings
    settings = Settings()

    # Initialize MongoDB client
    db_client = MongoDBClient(uri=settings.mongodb_uri, db_name=settings.mongodb_name)

    # Initialize and start the scheduler
    scheduler = TaskScheduler(db_client, settings)
    scheduler.start()

    try:
        # Keep the main thread alive
        print("Press Ctrl+C to exit.")
        while True:
            pass
    except (KeyboardInterrupt, SystemExit):
        scheduler.stop()
        db_client.close_connection()

if __name__ == "__main__":
    main()
