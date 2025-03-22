# YouTube Playlist Organizer

YouTubeの動画を機械学習を用いて自動で適切なプレイリストに振り分けるWebアプリケーション

## 機能

- YouTube動画の管理
- プレイリストの作成・編集
- 機械学習による動画の自動分類（開発予定）
- ユーザー認証

## 技術スタック

### バックエンド
- Python 3.9+
- FastAPI
- SQLAlchemy
- YouTube Data API

### フロントエンド
- Next.js
- TypeScript
- Tailwind CSS

## セットアップ

### バックエンド

1. 依存関係のインストール
```bash
cd backend
pip install -r requirements.txt
```

2. 環境変数の設定
`.env`ファイルをbackendディレクトリに作成し、以下の変数を設定：
```
YOUTUBE_API_KEY=your_api_key
SECRET_KEY=your_secret_key
```

3. サーバーの起動
```bash
cd backend
uvicorn app.main:app --reload
```

### フロントエンド

1. 依存関係のインストール
```bash
cd frontend
npm install
```

2. 開発サーバーの起動
```bash
npm run dev
```

## API ドキュメント

FastAPI の自動生成されたドキュメントは以下のURLで確認できます：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc 