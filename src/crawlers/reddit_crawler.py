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

    def store_posts(self, posts, keyword):
        collection_name = "reddit"
        collection = self.db_client.db[collection_name]

        if collection_name not in self.db_client.db.list_collection_names():
            print(f"[Reddit] Creating collection: {collection_name}")
            collection.create_index("url", unique=True)

        for post in posts:
            post["name"] = keyword
            try:
                collection.insert_one(post)
                print(f"[Reddit] Inserted: {post['title']} for {keyword} in {collection_name}")
            except Exception as e:
                print(f"[Reddit] Duplicate or error: {post['title']} for {keyword} in {collection_name} -> {e}")

