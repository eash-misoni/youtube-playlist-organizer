from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import relationship
from .base import BaseModel

class User(BaseModel):
    __tablename__ = "users"

    email = Column(String, unique=True, index=True)
    google_id = Column(String, unique=True)
    name = Column(String)
    picture_url = Column(String)  # プロフィール画像のURL
    youtube_access_token = Column(String)
    youtube_refresh_token = Column(String)
    token_expires_at = Column(DateTime)

    # リレーションシップ
    playlists = relationship("Playlist", back_populates="user", passive_deletes=True)
    classifications = relationship("Classification", back_populates="user", passive_deletes=True)
    classification_rules = relationship("ClassificationRule", back_populates="user", passive_deletes=True)
    classification_histories = relationship("ClassificationHistory", back_populates="user", passive_deletes=True) 