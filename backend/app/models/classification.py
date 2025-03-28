from sqlalchemy import Column, Integer, String, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from .base import BaseModel

class Classification(BaseModel):
    __tablename__ = "classifications"
    
    video_id = Column(Integer, ForeignKey("videos.id", ondelete="CASCADE"), nullable=False)
    playlist_id = Column(Integer, ForeignKey("playlists.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    confidence = Column(Float, nullable=True)
    status = Column(String, nullable=False)  # pending, completed, failed

    # リレーションシップ
    video = relationship("Video", back_populates="classifications", passive_deletes=True)
    playlist = relationship("Playlist", back_populates="classifications", passive_deletes=True)
    user = relationship("User", back_populates="classifications", passive_deletes=True)

class ClassificationRule(BaseModel):
    __tablename__ = "classification_rules"
    
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    playlist_id = Column(Integer, ForeignKey("playlists.id", ondelete="CASCADE"), nullable=False)
    rule_type = Column(String, nullable=False)  # keyword, tag, channel, etc.
    rule_value = Column(String, nullable=False)
    priority = Column(Integer, nullable=False)

    # リレーションシップ
    user = relationship("User", back_populates="classification_rules", passive_deletes=True)
    playlist = relationship("Playlist", back_populates="classification_rules", passive_deletes=True)

class ClassificationHistory(BaseModel):
    __tablename__ = "classification_histories"
    
    video_id = Column(Integer, ForeignKey("videos.id", ondelete="CASCADE"), nullable=False)
    playlist_id = Column(Integer, ForeignKey("playlists.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    action = Column(String, nullable=False)  # add, remove, modify

    # リレーションシップ
    video = relationship("Video", back_populates="classification_histories", passive_deletes=True)
    playlist = relationship("Playlist", back_populates="classification_histories", passive_deletes=True)
    user = relationship("User", back_populates="classification_histories", passive_deletes=True) 