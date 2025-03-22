from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # アプリケーション設定
    APP_NAME: str = "YouTube Playlist Organizer"
    DEBUG: bool = True
    
    # YouTube API設定
    YOUTUBE_API_KEY: str = ""
    
    # データベース設定
    DATABASE_URL: str = "sqlite:///./youtube_playlist.db"
    
    # JWT設定
    SECRET_KEY: str = "your-secret-key-here"  # 本番環境では必ず変更してください
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"

settings = Settings() 