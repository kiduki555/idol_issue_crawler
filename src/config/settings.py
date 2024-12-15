from pydantic import BaseSettings

class Settings(BaseSettings):
    # MongoDB Settings
    mongodb_uri: str
    mongodb_name: str

    # DCInside Settings
    dcinside_gallery_id: str
    dcinside_interval: int = 10  # in minutes

    # FM Korea Settings
    fm_korea_board_id: str
    fm_korea_interval: int = 10  # in minutes

    # X (Twitter) Settings
    x_api_key: str
    x_api_secret: str
    x_access_token: str
    x_access_secret: str
    x_query: str
    x_interval: int = 15  # in minutes

    # Reddit Settings
    reddit_client_id: str
    reddit_client_secret: str
    reddit_user_agent: str
    reddit_subreddit: str
    reddit_interval: int = 15  # in minutes

    class Config:
        env_file = ".env"
