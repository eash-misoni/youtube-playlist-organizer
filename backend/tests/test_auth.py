import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal, engine
from app.models.base import Base
from app.models.user import User
from app.config import settings

# テスト用のデータベースを作成
Base.metadata.create_all(bind=engine)

client = TestClient(app)

@pytest.fixture
def db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_auth_test_endpoint():
    """認証テストエンドポイントのテスト"""
    response = client.get("/auth/test")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "client_id" in data
    assert "redirect_uri" in data
    assert data["client_id"] == settings.GOOGLE_CLIENT_ID
    assert data["redirect_uri"] == settings.GOOGLE_REDIRECT_URI

def test_google_auth_start():
    """Google認証開始エンドポイントのテスト"""
    response = client.get("/auth/google", allow_redirects=False)
    assert response.status_code == 307  # リダイレクト
    assert "accounts.google.com" in response.headers["location"]

def test_google_auth_callback_invalid_code():
    """無効な認証コードでのコールバックテスト"""
    response = client.get("/auth/google/callback?code=invalid_code")
    assert response.status_code == 400

def test_get_current_user_no_token():
    """トークンなしでのユーザー情報取得テスト"""
    response = client.get("/auth/me")
    assert response.status_code == 401

def test_get_current_user_invalid_token():
    """無効なトークンでのユーザー情報取得テスト"""
    response = client.get("/auth/me", headers={"Authorization": "Bearer invalid_token"})
    assert response.status_code == 401

def test_user_model(db):
    """ユーザーモデルのテスト"""
    # テスト用のユーザーを作成
    test_user = User(
        email="test@example.com",
        name="Test User",
        picture_url="https://example.com/picture.jpg",
        google_id="test_google_id",
        youtube_access_token="test_access_token",
        youtube_refresh_token="test_refresh_token"
    )
    db.add(test_user)
    db.commit()
    db.refresh(test_user)

    # ユーザー情報の検証
    assert test_user.email == "test@example.com"
    assert test_user.name == "Test User"
    assert test_user.picture_url == "https://example.com/picture.jpg"
    assert test_user.google_id == "test_google_id"
    assert test_user.youtube_access_token == "test_access_token"
    assert test_user.youtube_refresh_token == "test_refresh_token"

    # データベースから取得して検証
    db_user = db.query(User).filter(User.email == "test@example.com").first()
    assert db_user is not None
    assert db_user.id == test_user.id

    # テストデータの削除
    db.delete(test_user)
    db.commit() 