from typing import Optional, List
from sqlalchemy.orm import Session
from .base import CRUDBase
from ..models.classification import Classification, ClassificationRule, ClassificationHistory

class CRUDClassification(CRUDBase[Classification]):
    def get_by_video_and_playlist(
        self, db: Session, *, video_id: str, playlist_id: str
    ) -> Optional[Classification]:
        return (
            db.query(Classification)
            .filter(
                Classification.video_id == video_id,
                Classification.playlist_id == playlist_id
            )
            .first()
        )

    def get_by_user(
        self, db: Session, *, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[Classification]:
        return (
            db.query(Classification)
            .filter(Classification.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_status(
        self, db: Session, *, status: str, skip: int = 0, limit: int = 100
    ) -> List[Classification]:
        return (
            db.query(Classification)
            .filter(Classification.status == status)
            .offset(skip)
            .limit(limit)
            .all()
        )

class CRUDClassificationRule(CRUDBase[ClassificationRule]):
    def get_by_user_and_playlist(
        self, db: Session, *, user_id: int, playlist_id: str
    ) -> List[ClassificationRule]:
        return (
            db.query(ClassificationRule)
            .filter(
                ClassificationRule.user_id == user_id,
                ClassificationRule.playlist_id == playlist_id
            )
            .all()
        )

    def get_by_priority(
        self, db: Session, *, user_id: int, playlist_id: str
    ) -> List[ClassificationRule]:
        return (
            db.query(ClassificationRule)
            .filter(
                ClassificationRule.user_id == user_id,
                ClassificationRule.playlist_id == playlist_id
            )
            .order_by(ClassificationRule.priority)
            .all()
        )

class CRUDClassificationHistory(CRUDBase[ClassificationHistory]):
    def get_by_user(
        self, db: Session, *, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[ClassificationHistory]:
        return (
            db.query(ClassificationHistory)
            .filter(ClassificationHistory.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_video_and_playlist(
        self, db: Session, *, video_id: str, playlist_id: str
    ) -> List[ClassificationHistory]:
        return (
            db.query(ClassificationHistory)
            .filter(
                ClassificationHistory.video_id == video_id,
                ClassificationHistory.playlist_id == playlist_id
            )
            .all()
        )

classification = CRUDClassification(Classification)
classification_rule = CRUDClassificationRule(ClassificationRule)
classification_history = CRUDClassificationHistory(ClassificationHistory) 