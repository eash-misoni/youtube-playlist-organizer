import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from app.models.user import User
from app.models.playlist import Playlist
from app.models.video import Video
from app.models.classification import Classification, ClassificationRule, ClassificationHistory
from app.crud import user, playlist, video, classification, classification_rule, classification_history
from app.models.base import BaseModel
from datetime import datetime, UTC

# テスト用のデータベース設定
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# SQLiteの外部キー制約を有効にする
def _fk_pragma_on_connect(dbapi_con, con_record):
    dbapi_con.execute('pragma foreign_keys=ON')

event.listen(engine, 'connect', _fk_pragma_on_connect)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    """テスト用のデータベースセッションを作成"""
    BaseModel.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        BaseModel.metadata.drop_all(bind=engine)

# テストデータ
test_user_data = {
    "email": "test@example.com",
    "google_id": "test_google_id",
    "name": "Test User",
    "youtube_access_token": "test_access_token",
    "youtube_refresh_token": "test_refresh_token",
    "token_expires_at": datetime.now(UTC)
}

test_playlist_data = {
    "youtube_playlist_id": "PL1234567890",
    "title": "Test Playlist",
    "description": "Test Description"
}

test_video_data = {
    "youtube_video_id": "test_video_id",
    "title": "Test Video",
    "description": "Test Description",
    "thumbnail_url": "https://example.com/thumbnail.jpg",
    "channel_id": "test_channel_id",
    "channel_title": "Test Channel",
    "published_at": datetime.now(UTC),
    "duration": "PT1H2M3S",
    "view_count": 1000,
    "like_count": 100,
    "tags": ["test", "video"]
}

# テストデータ追加
test_classification_rule_data = {
    "rule_type": "keyword",
    "rule_value": "プログラミング",
    "priority": 1
}

test_classification_history_data = {
    "action": "add"  # add, remove, modify
}

# User CRUD Tests
def test_create_user(db_session: Session):
    user_obj = user.create(db_session, obj_in=test_user_data)
    assert user_obj.email == test_user_data["email"]
    assert user_obj.google_id == test_user_data["google_id"]
    assert user_obj.name == test_user_data["name"]

def test_get_user(db_session: Session):
    user_obj = user.create(db_session, obj_in=test_user_data)
    retrieved_user = user.get(db_session, id=user_obj.id)
    assert retrieved_user.id == user_obj.id
    assert retrieved_user.email == user_obj.email

def test_get_user_by_email(db_session: Session):
    user_obj = user.create(db_session, obj_in=test_user_data)
    retrieved_user = user.get_by_email(db_session, email=test_user_data["email"])
    assert retrieved_user.id == user_obj.id
    assert retrieved_user.email == user_obj.email

def test_update_user(db_session: Session):
    user_obj = user.create(db_session, obj_in=test_user_data)
    update_data = {"name": "Updated Name"}
    updated_user = user.update(db_session, db_obj=user_obj, obj_in=update_data)
    assert updated_user.name == "Updated Name"

def test_delete_user(db_session: Session):
    user_obj = user.create(db_session, obj_in=test_user_data)
    deleted_user = user.delete(db_session, id=user_obj.id)
    assert deleted_user.id == user_obj.id
    assert user.get(db_session, id=user_obj.id) is None

# Playlist CRUD Tests
def test_create_playlist(db_session: Session):
    user_obj = user.create(db_session, obj_in=test_user_data)
    playlist_data = {**test_playlist_data, "user_id": user_obj.id}
    playlist_obj = playlist.create(db_session, obj_in=playlist_data)
    assert playlist_obj.youtube_playlist_id == playlist_data["youtube_playlist_id"]
    assert playlist_obj.title == playlist_data["title"]
    assert playlist_obj.user_id == user_obj.id

def test_get_playlist_by_youtube_id(db_session: Session):
    user_obj = user.create(db_session, obj_in=test_user_data)
    playlist_data = {**test_playlist_data, "user_id": user_obj.id}
    playlist_obj = playlist.create(db_session, obj_in=playlist_data)
    retrieved_playlist = playlist.get_by_youtube_id(db_session, youtube_id=playlist_data["youtube_playlist_id"])
    assert retrieved_playlist.id == playlist_obj.id
    assert retrieved_playlist.youtube_playlist_id == playlist_obj.youtube_playlist_id

def test_get_playlists_by_user(db_session: Session):
    user_obj = user.create(db_session, obj_in=test_user_data)
    playlist_data = {**test_playlist_data, "user_id": user_obj.id}
    playlist_obj = playlist.create(db_session, obj_in=playlist_data)
    playlists = playlist.get_by_user_id(db_session, user_id=user_obj.id)
    assert len(playlists) == 1
    assert playlists[0].id == playlist_obj.id

# Video CRUD Tests
def test_create_video(db_session: Session):
    video_obj = video.create(db_session, obj_in=test_video_data)
    assert video_obj.youtube_video_id == test_video_data["youtube_video_id"]
    assert video_obj.title == test_video_data["title"]
    assert video_obj.channel_id == test_video_data["channel_id"]

def test_get_video_by_youtube_id(db_session: Session):
    video_obj = video.create(db_session, obj_in=test_video_data)
    retrieved_video = video.get_by_youtube_id(db_session, youtube_id=test_video_data["youtube_video_id"])
    assert retrieved_video.id == video_obj.id
    assert retrieved_video.youtube_video_id == video_obj.youtube_video_id

def test_update_video_stats(db_session: Session):
    video_obj = video.create(db_session, obj_in=test_video_data)
    updated_video = video.update_stats(
        db_session, db_obj=video_obj, view_count=2000, like_count=200
    )
    assert updated_video.view_count == 2000
    assert updated_video.like_count == 200

# Classification CRUD Tests
def test_create_classification(db_session: Session):
    user_obj = user.create(db_session, obj_in=test_user_data)
    playlist_obj = playlist.create(db_session, obj_in={**test_playlist_data, "user_id": user_obj.id})
    video_obj = video.create(db_session, obj_in=test_video_data)
    
    classification_data = {
        "video_id": video_obj.id,
        "playlist_id": playlist_obj.id,
        "user_id": user_obj.id,
        "status": "pending"
    }
    classification_obj = classification.create(db_session, obj_in=classification_data)
    assert classification_obj.video_id == video_obj.id
    assert classification_obj.playlist_id == playlist_obj.id
    assert classification_obj.user_id == user_obj.id
    assert classification_obj.status == "pending"

def test_get_classification_by_video_and_playlist(db_session: Session):
    user_obj = user.create(db_session, obj_in=test_user_data)
    playlist_obj = playlist.create(db_session, obj_in={**test_playlist_data, "user_id": user_obj.id})
    video_obj = video.create(db_session, obj_in=test_video_data)
    
    classification_data = {
        "video_id": video_obj.id,
        "playlist_id": playlist_obj.id,
        "user_id": user_obj.id,
        "status": "pending"
    }
    classification_obj = classification.create(db_session, obj_in=classification_data)
    retrieved_classification = classification.get_by_video_and_playlist(
        db_session, video_id=video_obj.id, playlist_id=playlist_obj.id
    )
    assert retrieved_classification.id == classification_obj.id
    assert retrieved_classification.video_id == video_obj.id
    assert retrieved_classification.playlist_id == playlist_obj.id

# Classification Rule Tests
def test_create_classification_rule(db_session: Session):
    user_obj = user.create(db_session, obj_in=test_user_data)
    playlist_obj = playlist.create(db_session, obj_in={**test_playlist_data, "user_id": user_obj.id})
    
    rule_data = {
        **test_classification_rule_data,
        "user_id": user_obj.id,
        "playlist_id": playlist_obj.id
    }
    rule_obj = classification_rule.create(db_session, obj_in=rule_data)
    
    assert rule_obj.rule_type == rule_data["rule_type"]
    assert rule_obj.rule_value == rule_data["rule_value"]
    assert rule_obj.priority == rule_data["priority"]
    assert rule_obj.user_id == user_obj.id
    assert rule_obj.playlist_id == playlist_obj.id

def test_get_classification_rules_by_user_and_playlist(db_session: Session):
    user_obj = user.create(db_session, obj_in=test_user_data)
    playlist_obj = playlist.create(db_session, obj_in={**test_playlist_data, "user_id": user_obj.id})
    
    # 2つのルールを作成
    rule_data1 = {
        **test_classification_rule_data,
        "user_id": user_obj.id,
        "playlist_id": playlist_obj.id,
        "priority": 1
    }
    rule_data2 = {
        **test_classification_rule_data,
        "user_id": user_obj.id,
        "playlist_id": playlist_obj.id,
        "rule_value": "Python",
        "priority": 2
    }
    
    classification_rule.create(db_session, obj_in=rule_data1)
    classification_rule.create(db_session, obj_in=rule_data2)
    
    rules = classification_rule.get_by_user_and_playlist(
        db_session, user_id=user_obj.id, playlist_id=playlist_obj.id
    )
    assert len(rules) == 2

def test_get_classification_rules_by_priority(db_session: Session):
    user_obj = user.create(db_session, obj_in=test_user_data)
    playlist_obj = playlist.create(db_session, obj_in={**test_playlist_data, "user_id": user_obj.id})
    
    # 優先度の異なる2つのルールを作成
    rule_data1 = {
        **test_classification_rule_data,
        "user_id": user_obj.id,
        "playlist_id": playlist_obj.id,
        "priority": 2
    }
    rule_data2 = {
        **test_classification_rule_data,
        "user_id": user_obj.id,
        "playlist_id": playlist_obj.id,
        "rule_value": "Python",
        "priority": 1
    }
    
    classification_rule.create(db_session, obj_in=rule_data1)
    classification_rule.create(db_session, obj_in=rule_data2)
    
    rules = classification_rule.get_by_priority(
        db_session, user_id=user_obj.id, playlist_id=playlist_obj.id
    )
    assert len(rules) == 2
    assert rules[0].priority < rules[1].priority

# Classification History Tests
def test_create_classification_history(db_session: Session):
    user_obj = user.create(db_session, obj_in=test_user_data)
    playlist_obj = playlist.create(db_session, obj_in={**test_playlist_data, "user_id": user_obj.id})
    video_obj = video.create(db_session, obj_in=test_video_data)
    
    history_data = {
        **test_classification_history_data,
        "user_id": user_obj.id,
        "playlist_id": playlist_obj.id,
        "video_id": video_obj.id
    }
    history_obj = classification_history.create(db_session, obj_in=history_data)
    
    assert history_obj.action == history_data["action"]
    assert history_obj.user_id == user_obj.id
    assert history_obj.playlist_id == playlist_obj.id
    assert history_obj.video_id == video_obj.id

def test_get_classification_history_by_user(db_session: Session):
    user_obj = user.create(db_session, obj_in=test_user_data)
    playlist_obj = playlist.create(db_session, obj_in={**test_playlist_data, "user_id": user_obj.id})
    video_obj = video.create(db_session, obj_in=test_video_data)
    
    # 2つの履歴を作成
    history_data1 = {
        **test_classification_history_data,
        "user_id": user_obj.id,
        "playlist_id": playlist_obj.id,
        "video_id": video_obj.id,
        "action": "add"
    }
    history_data2 = {
        **test_classification_history_data,
        "user_id": user_obj.id,
        "playlist_id": playlist_obj.id,
        "video_id": video_obj.id,
        "action": "remove"
    }
    
    classification_history.create(db_session, obj_in=history_data1)
    classification_history.create(db_session, obj_in=history_data2)
    
    histories = classification_history.get_by_user(db_session, user_id=user_obj.id)
    assert len(histories) == 2

def test_get_classification_history_by_video_and_playlist(db_session: Session):
    user_obj = user.create(db_session, obj_in=test_user_data)
    playlist_obj = playlist.create(db_session, obj_in={**test_playlist_data, "user_id": user_obj.id})
    video_obj = video.create(db_session, obj_in=test_video_data)
    
    # 2つの履歴を作成
    history_data1 = {
        **test_classification_history_data,
        "user_id": user_obj.id,
        "playlist_id": playlist_obj.id,
        "video_id": video_obj.id,
        "action": "add"
    }
    history_data2 = {
        **test_classification_history_data,
        "user_id": user_obj.id,
        "playlist_id": playlist_obj.id,
        "video_id": video_obj.id,
        "action": "modify"
    }
    
    classification_history.create(db_session, obj_in=history_data1)
    classification_history.create(db_session, obj_in=history_data2)
    
    histories = classification_history.get_by_video_and_playlist(
        db_session, video_id=video_obj.id, playlist_id=playlist_obj.id
    )
    assert len(histories) == 2 