from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship, validates
from sqlalchemy.sql import func
from .base import BaseModel
from datetime import datetime
import re

# プレイリストと動画の関連テーブル
playlist_videos = Table(
    'playlist_videos',
    BaseModel.metadata,
    Column('playlist_id', Integer, ForeignKey('playlists.id', ondelete='CASCADE')),
    Column('video_id', Integer, ForeignKey('videos.id', ondelete='CASCADE'))
)

class Playlist(BaseModel):
    __tablename__ = "playlists"

    youtube_playlist_id = Column(String(50), unique=True)  # YouTubeのプレイリストIDは通常短い
    title = Column(String(100))  # タイトルは100文字以内
    description = Column(String(500))  # 説明は500文字以内
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))

    # リレーションシップ
    user = relationship("User", back_populates="playlists", passive_deletes=True)
    videos = relationship("Video", secondary=playlist_videos, back_populates="playlists")
    classifications = relationship("Classification", back_populates="playlist", cascade="all, delete-orphan", passive_deletes=True)
    classification_rules = relationship("ClassificationRule", back_populates="playlist", cascade="all, delete-orphan", passive_deletes=True)
    classification_histories = relationship("ClassificationHistory", back_populates="playlist", cascade="all, delete-orphan", passive_deletes=True)

    @validates('user_id')
    def validate_user_id(self, key, value):
        if value is not None and not isinstance(value, int):
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