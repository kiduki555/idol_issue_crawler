from pydantic import BaseModel, Field, ValidationError
from typing import Optional, List
from datetime import datetime

class BaseDataModel(BaseModel):
    """
    Base model for all data stored in MongoDB.
    """
    title: str = Field(..., description="The title of the post or content")
    content: Optional[str] = Field(None, description="The content of the post")
    url: str = Field(..., description="The URL of the post or content")
    source: str = Field(..., description="The source platform (e.g., dcinside, reddit, etc.)")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="The timestamp of data collection")
    view_count: Optional[int] = Field(0, description="Number of views")
    comment_count: Optional[int] = Field(0, description="Number of comments")
    sentiment_score: Optional[float] = Field(None, description="Sentiment analysis score (-1.0 to 1.0)")

class ControversyDataModel(BaseDataModel):
    """
    Model for controversy-related data.
    """
    controversy_score: Optional[float] = Field(None, description="Controversy score calculated from data")

class PositiveDataModel(BaseDataModel):
    """
    Model for positive-related data.
    """
    positive_score: Optional[float] = Field(None, description="Positive score calculated from data")

class YouTubeSnippetModel(BaseModel):
    """
    Model for YouTube snippet data.
    """
    video_id: str = Field(..., description="YouTube video ID")
    snippets: List[dict] = Field(..., description="List of video snippet information")
    title: str = Field(..., description="The title of the YouTube video")
    source: str = Field("youtube", description="The source platform")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="The timestamp of data collection")
