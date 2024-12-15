import tweepy
from src.db.mongo_client import MongoDBClient

class XCrawler:
    def __init__(self, db_client, api_key, api_secret, access_token, access_secret):
        self.db_client = db_client
        auth = tweepy.OAuthHandler(api_key, api_secret)
        auth.set_access_token(access_token, access_secret)
        self.client = tweepy.API(auth)

    def fetch_tweets(self, query, count=10):
        """
        Fetch tweets based on a search query.
        """
        tweets = self.client.search_tweets(q=query, count=count, lang="ko")
        posts = []
        for tweet in tweets:
            posts.append({
                "text": tweet.text,
                "author": tweet.user.screen_name,
                "url": f"https://twitter.com/{tweet.user.screen_name}/status/{tweet.id}",
                "source": "x"
            })
        self.store_posts(posts)

    def store_posts(self, posts, keyword):
        collection_name = "x"
        collection = self.db_client.db[collection_name]

        # Ensure collection exists and has necessary indexes
        if collection_name not in self.db_client.db.list_collection_names():
            print(f"[X] Creating collection: {collection_name}")
            collection.create_index("url", unique=True)

        for post in posts:
            post["name"] = keyword
            try:
                collection.insert_one(post)
                print(f"[X] Inserted: {post['title']} for {keyword} in {collection_name}")
            except Exception as e:
                print(f"[X] Duplicate or error: {post['title']} for {keyword} in {collection_name} -> {e}")
