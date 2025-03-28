from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.security import OAuth2AuthorizationCodeBearer
from google.oauth2 import id_token
from google.auth.transport import requests
from ..config import settings
from ..models.user import User
from ..database import get_db
from sqlalchemy.orm import Session
from fastapi.responses import RedirectResponse
import httpx
import json

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl="https://accounts.google.com/o/oauth2/v2/auth",
    tokenUrl="https://oauth2.googleapis.com/token",
    scopes={
        "openid": "OpenID Connect scope",
        "https://www.googleapis.com/auth/youtube.readonly": "YouTube Data API scope"
    }
)

@router.get("/test")
async def test_auth():
    """
    認証テスト用のエンドポイント
    """
    return {
        "message": "認証エンドポイントは正常に動作しています",
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI
    }

@router.get("/google")
async def google_auth_start():
    """
    Google OAuth2認証を開始します
    """
    auth_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth"
        f"?response_type=code"
        f"&client_id={settings.GOOGLE_CLIENT_ID}"
        f"&redirect_uri={settings.GOOGLE_REDIRECT_URI}"
        f"&scope=openid email profile https://www.googleapis.com/auth/youtube.readonly"
        f"&access_type=offline"
        f"&prompt=consent"
    )
    return RedirectResponse(auth_url)

@router.get("/google/callback")
async def google_auth_callback(code: str, db: Session = Depends(get_db)):
    """
    Google OAuth2認証のコールバックを処理します
    """
    try:
        # 認証コードを使用してトークンを取得
        token_url = "https://oauth2.googleapis.com/token"
        token_data = {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": settings.GOOGLE_REDIRECT_URI
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(token_url, data=token_data)
            token_response = response.json()
            
            if "error" in token_response:
                print(f"Token Error Response: {json.dumps(token_response, indent=2)}")
                raise HTTPException(
                    status_code=400,
                    detail=f"トークン取得エラー: {token_response['error']}"
                )
            
            if "id_token" not in token_response:
                print(f"Token Response without id_token: {json.dumps(token_response, indent=2)}")
                raise HTTPException(
                    status_code=400,
                    detail="IDトークンが取得できませんでした"
                )

            try:
                # IDトークンの検証
                idinfo = id_token.verify_oauth2_token(
                    token_response["id_token"], 
                    requests.Request(), 
                    settings.GOOGLE_CLIENT_ID
                )
            except Exception as e:
                print(f"Token Verification Error: {str(e)}")
                raise HTTPException(
                    status_code=400,
                    detail=f"トークンの検証に失敗しました: {str(e)}"
                )

            # ユーザー情報の取得
            email = idinfo.get('email')
            if not email:
                raise HTTPException(
                    status_code=400,
                    detail="メールアドレスが取得できませんでした"
                )

            name = idinfo.get('name', '')
            picture = idinfo.get('picture', '')
            google_id = idinfo.get('sub', '')  # GoogleのユーザーID

            # データベースでユーザーを検索または作成
            user = db.query(User).filter(User.email == email).first()
            if not user:
                user = User(
                    email=email,
                    name=name,
                    picture_url=picture,
                    google_id=google_id,
                    youtube_access_token=token_response.get("access_token", ""),
                    youtube_refresh_token=token_response.get("refresh_token", ""),
                    token_expires_at=None  # TODO: トークンの有効期限を設定
                )
                db.add(user)
            else:
                # 既存ユーザーの情報を更新
                user.name = name
                user.picture_url = picture
                user.google_id = google_id
                user.youtube_access_token = token_response.get("access_token", "")
                user.youtube_refresh_token = token_response.get("refresh_token", "")
                user.token_expires_at = None  # TODO: トークンの有効期限を設定

            db.commit()
            db.refresh(user)

            return {
                "access_token": token_response["access_token"],
                "id_token": token_response["id_token"],
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "name": user.name,
                    "picture_url": user.picture_url,
                    "google_id": user.google_id
                }
            }

    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"Unexpected Error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"予期せぬエラーが発生しました: {str(e)}"
        )

@router.get("/me")
async def get_current_user(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    現在のユーザー情報を取得します
    """
    try:
        # リクエストヘッダーからトークンを取得
        token = request.headers.get("Authorization")
        if not token or not token.startswith("Bearer "):
            raise HTTPException(
                status_code=401,
                detail="認証が必要です"
            )
        
        token = token.split(" ")[1]
        
        # トークンの検証
        idinfo = id_token.verify_oauth2_token(
            token, 
            requests.Request(), 
            settings.GOOGLE_CLIENT_ID
        )

        # ユーザー情報の取得
        email = idinfo['email']
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            raise HTTPException(
                status_code=404,
                detail="ユーザーが見つかりません"
            )

        return {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "picture_url": user.picture_url
        }

    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail="認証に失敗しました"
        ) 