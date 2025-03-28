from sqlalchemy import Column, Integer, String, DateTime, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import BaseModel

class Video(BaseModel):
    __tablename__ = "videos"

    youtube_video_id = Column(String, unique=True)
    title = Column(String)
    description = Column(Text)
    thumbnail_url = Column(String)
    channel_id = Column(String)
    channel_title = Column(String)
    published_at = Column(DateTime)
    duration = Column(String)
    view_count = Column(Integer)
    like_count = Column(Integer)
    tags = Column(JSON)

    # リレーションシップ
    playlists = relationship("Playlist", secondary="playlist_videos", back_populates="videos")
    classifications = relationship("Classification", back_populates="video")
    classification_histories = relationship("ClassificationHistory", back_populates="video") 