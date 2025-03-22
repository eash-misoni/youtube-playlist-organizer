from fastapi import APIRouter, HTTPException
from googleapiclient.discovery import build
from ..config import settings

router = APIRouter(
    prefix="/youtube",
    tags=["youtube"]
)

def get_youtube_client():
    try:
        return build('youtube', 'v3', developerKey=settings.YOUTUBE_API_KEY)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search")
async def search_videos(query: str, max_results: int = 10):
    """
    指定したクエリでYouTube動画を検索します
    """
    youtube = get_youtube_client()
    try:
        request = youtube.search().list(
            part="snippet",
            q=query,
            type="video",
            maxResults=max_results
        )
        response = request.execute()
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/playlists")
async def get_playlists():
    """
    認証済みユーザーのプレイリスト一覧を取得します
    """
    youtube = get_youtube_client()
    try:
        request = youtube.playlists().list(
            part="snippet",
            mine=True,
            maxResults=50
        )
        response = request.execute()
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 