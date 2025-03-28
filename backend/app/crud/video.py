from typing import Optional, List
from sqlalchemy.orm import Session
from .base import CRUDBase
from ..models.video import Video

class CRUDVideo(CRUDBase[Video]):
    def get_by_youtube_id(self, db: Session, *, youtube_id: str) -> Optional[Video]:
        return db.query(Video).filter(Video.youtube_video_id == youtube_id).first()

    def get_by_channel_id(
        self, db: Session, *, channel_id: str, skip: int = 0, limit: int = 100
    ) -> List[Video]:
        return (
            db.query(Video)
            .filter(Video.channel_id == channel_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_title(
        self, db: Session, *, title: str, skip: int = 0, limit: int = 100
    ) -> List[Video]:
        return (
            db.query(Video)
            .filter(Video.title.ilike(f"%{title}%"))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def update_stats(
        self,
        db: Session,
        *,
        db_obj: Video,
        view_count: Optional[int] = None,
        like_count: Optional[int] = None
    ) -> Video:
        if view_count is not None:
            db_obj.view_count = view_count
        if like_count is not None:
            db_obj.like_count = like_count
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

video = CRUDVideo(Video) 