from typing import Optional, List
from sqlalchemy.orm import Session
from .base import CRUDBase
from ..models.playlist import Playlist

class CRUDPlaylist(CRUDBase[Playlist]):
    def get_by_youtube_id(self, db: Session, *, youtube_id: str) -> Optional[Playlist]:
        return db.query(Playlist).filter(Playlist.youtube_playlist_id == youtube_id).first()

    def get_by_user_id(
        self, db: Session, *, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[Playlist]:
        return (
            db.query(Playlist)
            .filter(Playlist.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_title(
        self, db: Session, *, title: str, user_id: int
    ) -> Optional[Playlist]:
        return (
            db.query(Playlist)
            .filter(Playlist.title == title, Playlist.user_id == user_id)
            .first()
        )

    def add_video(self, db: Session, *, playlist: Playlist, video_id: int) -> Playlist:
        playlist.videos.append(video_id)
        db.add(playlist)
        db.commit()
        db.refresh(playlist)
        return playlist

    def remove_video(self, db: Session, *, playlist: Playlist, video_id: int) -> Playlist:
        playlist.videos.remove(video_id)
        db.add(playlist)
        db.commit()
        db.refresh(playlist)
        return playlist

playlist = CRUDPlaylist(Playlist) 