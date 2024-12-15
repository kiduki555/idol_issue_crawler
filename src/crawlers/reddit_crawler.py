import praw
from src.db.mongo_client import MongoDBClient

class RedditCrawler:
    def __init__(self, db_client, client_id, client_secret, user_agent):
        self.db_client = db_client
        self.reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )

    def fetch_posts(self, subreddit_name, limit=10):
        """
        Fetch posts from a subreddit.
        """
        subreddit = self.reddit.subreddit(subreddit_name)
        posts = []
        for submission in subreddit.hot(limit=limit):
            posts.append({
                "title": submission.title,
                "url": submission.url,
                "author": submission.author.name if submission.author else "Unknown",
                "source": "reddit"
            })
        self.store_posts(posts)

    def store_posts(self, posts):
        """
        Store parsed posts in MongoDB.
        """
        for post in posts:
            if self.db_client.insert_data("reddit", post):
                print(f"Inserted: {post['title']}")
            else:
                print(f"Duplicate skipped: {post['title']}")
