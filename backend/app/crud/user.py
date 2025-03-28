from typing import Optional
from sqlalchemy.orm import Session
from .base import CRUDBase
from ..models.user import User

class CRUDUser(CRUDBase[User]):
    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()

    def get_by_google_id(self, db: Session, *, google_id: str) -> Optional[User]:
        return db.query(User).filter(User.google_id == google_id).first()

    def get_by_youtube_token(self, db: Session, *, access_token: str) -> Optional[User]:
        return db.query(User).filter(User.youtube_access_token == access_token).first()

    def update_youtube_tokens(
        self,
        db: Session,
        *,
        db_obj: User,
        access_token: str,
        refresh_token: str,
        expires_at: Optional[str] = None
    ) -> User:
        db_obj.youtube_access_token = access_token
        db_obj.youtube_refresh_token = refresh_token
        if expires_at:
            db_obj.token_expires_at = expires_at
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

user = CRUDUser(User) 