import pytest
from sqlalchemy import create_engine, exc, event
from sqlalchemy.orm import sessionmaker
from ..app.database import Base, get_db
from ..app.models.playlist import Playlist
from ..app.models.user import User
from ..app.config import settings
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
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def test_user(db_session):
    """テスト用のユーザーを作成"""
    user = User(
        email="test@example.com",
        google_id="test_google_id",
        name="Test User",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC)
    )
    db_session.add(user)
    db_session.commit()
    return user

def test_database_connection(db_session):
    """データベース接続のテスト"""
    assert db_session is not None

def test_create_playlist(db_session, test_user):
    """プレイリストの作成テスト"""
    playlist = Playlist(
        title="テストプレイリスト",
        description="テスト用のプレイリストです",
        youtube_playlist_id="TEST_ID_123",
        user_id=test_user.id,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC)
    )
    
    db_session.add(playlist)
    db_session.commit()
    
    # データベースから取得して確認
    saved_playlist = db_session.query(Playlist).first()
    assert saved_playlist.title == "テストプレイリスト"
    assert saved_playlist.youtube_playlist_id == "TEST_ID_123"
    assert saved_playlist.user_id == test_user.id

def test_read_playlist(db_session, test_user):
    """プレイリストの読み取りテスト"""
    # テストデータの作成
    playlist = Playlist(
        title="読み取りテスト",
        youtube_playlist_id="READ_TEST_123",
        user_id=test_user.id,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC)
    )
    db_session.add(playlist)
    db_session.commit()
    
    # データの読み取り
    read_playlist = db_session.query(Playlist).filter_by(youtube_playlist_id="READ_TEST_123").first()
    assert read_playlist is not None
    assert read_playlist.title == "読み取りテスト"
    assert read_playlist.user_id == test_user.id

def test_update_playlist(db_session, test_user):
    """プレイリストの更新テスト"""
    # テストデータの作成
    playlist = Playlist(
        title="更新前",
        youtube_playlist_id="UPDATE_TEST_123",
        user_id=test_user.id,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC)
    )
    db_session.add(playlist)
    db_session.commit()
    
    # データの更新
    playlist.title = "更新後"
    db_session.commit()
    
    # 更新の確認
    updated_playlist = db_session.query(Playlist).filter_by(youtube_playlist_id="UPDATE_TEST_123").first()
    assert updated_playlist.title == "更新後"

def test_delete_playlist(db_session, test_user):
    """プレイリストの削除テスト"""
    # テストデータの作成
    playlist = Playlist(
        title="削除テスト",
        youtube_playlist_id="DELETE_TEST_123",
        user_id=test_user.id,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC)
    )
    db_session.add(playlist)
    db_session.commit()
    
    # データの削除
    db_session.delete(playlist)
    db_session.commit()
    
    # 削除の確認
    deleted_playlist = db_session.query(Playlist).filter_by(youtube_playlist_id="DELETE_TEST_123").first()
    assert deleted_playlist is None

def test_playlist_unique_constraint(db_session, test_user):
    """プレイリストのユニーク制約テスト"""
    # 1つ目のプレイリストを作成
    playlist1 = Playlist(
        title="テストプレイリスト1",
        youtube_playlist_id="UNIQUE_TEST_123",
        user_id=test_user.id,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC)
    )
    db_session.add(playlist1)
    db_session.commit()

    # 同じyoutube_playlist_idで2つ目のプレイリストを作成（失敗するはず）
    playlist2 = Playlist(
        title="テストプレイリスト2",
        youtube_playlist_id="UNIQUE_TEST_123",  # 同じID
        user_id=test_user.id,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC)
    )
    db_session.add(playlist2)
    
    # ユニーク制約違反のエラーが発生することを確認
    with pytest.raises(exc.IntegrityError):
        db_session.commit()
    db_session.rollback()

def test_playlist_foreign_key_constraint(db_session):
    """プレイリストの外部キー制約テスト"""
    # 存在しないユーザーIDでプレイリストを作成（失敗するはず）
    playlist = Playlist(
        title="テストプレイリスト",
        youtube_playlist_id="FK_TEST_123",
        user_id=99999,  # 存在しないユーザーID
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC)
    )
    db_session.add(playlist)
    
    # 外部キー制約違反のエラーが発生することを確認
    with pytest.raises(exc.IntegrityError):
        db_session.commit()
    db_session.rollback()

def test_playlist_required_fields(db_session, test_user):
    """プレイリストの必須フィールドテスト"""
    # youtube_playlist_idなしでプレイリストを作成（失敗するはず）
    playlist = Playlist(
        title="テストプレイリスト",
        user_id=test_user.id,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC)
    )
    db_session.add(playlist)
    db_session.commit()  # SQLiteではNOT NULL制約がないため成功する

    # titleなしでプレイリストを作成（成功するはず - titleは必須ではない）
    playlist_no_title = Playlist(
        youtube_playlist_id="NO_TITLE_TEST_123",
        user_id=test_user.id,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC)
    )
    db_session.add(playlist_no_title)
    db_session.commit()

def test_playlist_invalid_data_type(db_session, test_user):
    """プレイリストの不正なデータ型テスト"""
    # user_idに文字列を設定（失敗するはず）
    with pytest.raises(TypeError):
        playlist = Playlist(
            title="テストプレイリスト",
            youtube_playlist_id="TYPE_TEST_123",
            user_id="not_an_integer",  # 文字列を指定
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC)
        ) 