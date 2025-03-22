from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import youtube

app = FastAPI(title="YouTube Playlist Organizer")

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # フロントエンドのURL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ルーターの追加
app.include_router(youtube.router)

@app.get("/")
async def root():
    return {"message": "YouTube Playlist Organizer API"} 