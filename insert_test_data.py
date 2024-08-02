from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import Session
from datetime import datetime
import pytz
from passlib.context import CryptContext
from db.db_config import Base, engine, SessionLocal  # db_configからインポート

# 日本時間（JST）を取得する関数
def jst_now():
    return datetime.now(pytz.timezone('Asia/Tokyo'))

# パスワードのハッシュ化のための設定
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_name = Column(String(225), unique=True, index=True)
    email = Column(String(225), unique=True, index=True)
    password = Column(String(225))
    type_id = Column(Integer)
    occupation_id = Column(String(225))
    overtime_id = Column(Integer)
    create_datetime = Column(DateTime, default=jst_now)
    update_datetime = Column(DateTime, default=jst_now, onupdate=jst_now)

# テーブルの作成
Base.metadata.create_all(bind=engine)

# テストデータの作成
test_data = [
    User(
        user_name="田中太郎",
        email="new_test1@example.com",
        password=pwd_context.hash("password1"),
        type_id=1,
        occupation_id="1",
        overtime_id=10
    ),
    User(
        user_name="山田花子",
        email="new_test2@example.com",
        password=pwd_context.hash("password2"),
        type_id=2,
        occupation_id="2",
        overtime_id=20
    )
]

# データベースにテストデータを挿入する関数
def insert_test_data(session: Session, data):
    # 既存のデータを削除
    session.query(User).delete()
    session.commit()

    for record in data:
        session.add(record)
    session.commit()

# メインプログラム
if __name__ == "__main__":
    # データベースセッションの作成
    db = SessionLocal()

    # テストデータの挿入
    insert_test_data(db, test_data)

    # セッションのクローズ
    db.close()
