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

    def store_posts(self, posts):
        """
        Store tweets in MongoDB.
        """
        for post in posts:
            if self.db_client.insert_data("x", post):
                print(f"Inserted tweet: {post['text']}")
            else:
                print(f"Duplicate skipped: {post['text']}")
