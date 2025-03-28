from app.database import SessionLocal
from app.models.user import User

def check_users():
    db = SessionLocal()
    try:
        users = db.query(User).all()
        print("\n=== ユーザー一覧 ===")
        for user in users:
            print(f"\nユーザーID: {user.id}")
            print(f"メールアドレス: {user.email}")
            print(f"名前: {user.name}")
            print(f"プロフィール画像URL: {user.picture_url}")
            print(f"Google ID: {user.google_id}")
            print(f"作成日時: {user.created_at}")
            print(f"更新日時: {user.updated_at}")
    finally:
        db.close()

if __name__ == "__main__":
    check_users() 