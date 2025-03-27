import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ..app.database import Base, get_db
from ..app.config import settings

# テスト用のデータベース設定
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
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

def test_database_connection(db_session):
    """データベース接続のテスト"""
    # セッションが正常に作成されていることを確認
    assert db_session is not None 