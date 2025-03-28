import pytest
from datetime import datetime, UTC
from sqlalchemy.exc import IntegrityError
from app.models.user import User
from app.models.playlist import Playlist
from app.models.video import Video
from app.models.classification import Classification, ClassificationRule, ClassificationHistory
from app.crud.user import user as crud_user
from app.crud.playlist import playlist as crud_playlist
from app.crud.video import video as crud_video
from app.crud.classification import classification as crud_classification
from .test_database import db_session

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
    "youtube_playlist_id": "test_playlist_id",
    "title": "Test Playlist",
    "description": "Test Description"
}

test_video_data = {
    "youtube_video_id": "test_video_id",
    "title": "Test Video",
    "description": "Test Description",
    "thumbnail_url": "https://example.com/thumbnail.jpg"
}

def test_transaction_rollback(db_session):
    """トランザクションのロールバックをテスト"""
    # ユーザーを作成
    user = crud_user.create(db_session, obj_in=test_user_data)
    
    try:
        # 意図的にエラーを発生させる
        playlist = crud_playlist.create(
            db_session,
            obj_in={**test_playlist_data, "user_id": -1}  # 存在しないユーザーID
        )
    except Exception:
        db_session.rollback()
    
    # ユーザーが作成されていることを確認
    user = crud_user.get_by_email(db_session, email=test_user_data["email"])
    assert user is not None
    
    # プレイリストが作成されていないことを確認
    playlist = crud_playlist.get_by_youtube_id(
        db_session,
        youtube_id=test_playlist_data["youtube_playlist_id"]
    )
    assert playlist is None

def test_concurrent_operations(db_session):
    """同時実行時の動作をテスト"""
    # ユーザーを作成
    user = crud_user.create(db_session, obj_in=test_user_data)
    
    # 複数のプレイリストを同時に作成
    playlist_data_list = [
        {**test_playlist_data, "youtube_playlist_id": f"test_playlist_{i}", "user_id": user.id}
        for i in range(3)
    ]
    
    playlists = []
    for playlist_data in playlist_data_list:
        playlist = crud_playlist.create(db_session, obj_in=playlist_data)
        playlists.append(playlist)
    
    # すべてのプレイリストが正しく作成されたことを確認
    assert len(playlists) == 3
    for i, playlist in enumerate(playlists):
        assert playlist.youtube_playlist_id == f"test_playlist_{i}"
        assert playlist.user_id == user.id

def test_complex_relationships(db_session):
    """複雑なリレーションシップの操作をテスト"""
    # ユーザーを作成
    user = crud_user.create(db_session, obj_in=test_user_data)
    
    # プレイリストを作成
    playlist = crud_playlist.create(
        db_session,
        obj_in={**test_playlist_data, "user_id": user.id}
    )
    
    # 動画を作成
    video = crud_video.create(db_session, obj_in=test_video_data)
    
    # プレイリストに動画を追加
    playlist.videos.append(video)
    
    # 分類を作成
    classification = crud_classification.create(
        db_session,
        obj_in={
            "user_id": user.id,
            "video_id": video.id,
            "playlist_id": playlist.id,
            "status": "completed",
            "confidence": 0.95
        }
    )
    
    # 分類ルールを作成
    rule = ClassificationRule(
        user_id=user.id,
        playlist_id=playlist.id,
        rule_type="keyword",
        rule_value="test",
        priority=1
    )
    db_session.add(rule)
    db_session.commit()
    
    # 分類履歴を作成
    history = ClassificationHistory(
        user_id=user.id,
        video_id=video.id,
        playlist_id=playlist.id,
        action="add"
    )
    db_session.add(history)
    db_session.commit()
    
    # リレーションシップが正しく設定されていることを確認
    assert len(user.playlists) == 1
    assert len(playlist.videos) == 1
    assert len(user.classifications) == 1
    assert len(user.classification_rules) == 1
    assert len(user.classification_histories) == 1

def test_cascade_delete(db_session):
    """カスケード削除の動作をテスト"""
    # ユーザーを作成
    user = crud_user.create(db_session, obj_in=test_user_data)
    
    # プレイリストを作成
    playlist = crud_playlist.create(
        db_session,
        obj_in={**test_playlist_data, "user_id": user.id}
    )
    
    # 動画を作成
    video = crud_video.create(db_session, obj_in=test_video_data)
    
    # プレイリストに動画を追加
    playlist.videos.append(video)
    
    # 分類を作成
    classification = crud_classification.create(
        db_session,
        obj_in={
            "user_id": user.id,
            "video_id": video.id,
            "playlist_id": playlist.id,
            "status": "completed",
            "confidence": 0.95
        }
    )

    # IDを保存
    playlist_id = playlist.id
    video_id = video.id
    classification_id = classification.id
    
    # ユーザーを削除
    crud_user.delete(db_session, id=user.id)
    db_session.commit()
    db_session.expire_all()
    
    # 関連するデータが削除されていることを確認
    assert crud_playlist.get(db_session, id=playlist_id) is None
    assert crud_video.get(db_session, id=video_id) is not None  # 動画は削除されない
    assert crud_classification.get(db_session, id=classification_id) is None

def test_unique_constraint_violation(db_session):
    """ユニーク制約違反のテスト"""
    # ユーザーを作成
    user = crud_user.create(db_session, obj_in=test_user_data)
    db_session.commit()
    
    # 同じメールアドレスでユーザーを作成しようとする
    with pytest.raises(IntegrityError):
        try:
            crud_user.create(db_session, obj_in=test_user_data)
            db_session.commit()
        except:
            db_session.rollback()
            raise
    
    # 同じGoogle IDでユーザーを作成しようとする
    with pytest.raises(IntegrityError):
        try:
            crud_user.create(
                db_session,
                obj_in={
                    **test_user_data,
                    "email": "different@example.com",
                    "google_id": test_user_data["google_id"]
                }
            )
            db_session.commit()
        except:
            db_session.rollback()
            raise 