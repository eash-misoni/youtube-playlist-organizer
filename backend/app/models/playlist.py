from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship, validates
from sqlalchemy.sql import func
from ..database import Base
from datetime import datetime
import re

# プレイリストと動画の関連テーブル
playlist_videos = Table(
    'playlist_videos',
    Base.metadata,
    Column('playlist_id', Integer, ForeignKey('playlists.id')),
    Column('video_id', Integer, ForeignKey('videos.id'))
)

class Playlist(Base):
    __tablename__ = "playlists"

    id = Column(Integer, primary_key=True, index=True)
    youtube_playlist_id = Column(String(50), unique=True)  # YouTubeのプレイリストIDは通常短い
    title = Column(String(100))  # タイトルは100文字以内
    description = Column(String(500))  # 説明は500文字以内
    user_id = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # リレーションシップ
    user = relationship("User", back_populates="playlists")
    videos = relationship("Video", secondary=playlist_videos, back_populates="playlists")

    @validates('user_id')
    def validate_user_id(self, key, value):
        if not isinstance(value, int):
            raise TypeError(f"{key} must be an integer")
        return value

    @validates('youtube_playlist_id')
    def validate_youtube_playlist_id(self, key, value):
        if not value:
            raise ValueError(f"{key} cannot be empty")
        if len(value) > 50:
            raise ValueError(f"{key} must be 50 characters or less")
        # YouTubeのプレイリストIDの形式をチェック（例：PLxxxxxxxxxx）
        if not re.match(r'^[A-Za-z0-9_-]{10,50}$', value):
            raise ValueError(f"{key} must be a valid YouTube playlist ID")
        return value

    @validates('title')
    def validate_title(self, key, value):
        if value and len(value) > 100:
            raise ValueError(f"{key} must be 100 characters or less")
        return value

    @validates('description')
    def validate_description(self, key, value):
        if value and len(value) > 500:
            raise ValueError(f"{key} must be 500 characters or less")
        return value

    @validates('created_at', 'updated_at')
    def validate_datetime(self, key, value):
        if not isinstance(value, datetime):
            raise TypeError(f"{key} must be a datetime object")
        if value.tzinfo is None:
            raise ValueError(f"{key} must be timezone-aware")
        return value 