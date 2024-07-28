from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
import pytz
from passlib.context import CryptContext

DATABASE_URL = "sqlite:///./heattech.db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 日本時間（JST）を取得する関数
def jst_now():
    return datetime.now(pytz.timezone('Asia/Tokyo'))

# パスワードのハッシュ化のための設定
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

class CopingMessage(Base):
    __tablename__ = "coping_message"

    coping_message_id = Column(Integer, primary_key=True, index=True)
    coping_id = Column(Integer)
    coping_message_text = Column(Text)
    selected = Column(Integer)
    satisfaction_score = Column(String(225))
    heart_rate_before = Column(Integer)
    heart_rate_after = Column(Integer)
    create_datetime = Column(DateTime, default=jst_now)
    update_datetime = Column(DateTime, default=jst_now, onupdate=jst_now)

class Usertable(Base):
    __tablename__ = "user_table"

    user_id = Column(Integer, primary_key=True, index=True)
    user_name = Column(String(225), unique=True, index=True)
    email = Column(String(225), unique=True, index=True)
    password = Column(String(225))
    type_id = Column(Integer)
    occupation_id = Column(String(225))
    overtime_id = Column(Integer)
    create_datetime = Column(DateTime, default=jst_now)
    update_datetime = Column(DateTime, default=jst_now, onupdate=jst_now)

Base.metadata.create_all(bind=engine)

# テストデータの作成
test_data = [
    Usertable(
        user_name="田中太郎",
        email="new_test1@example.com",  # 異なるメールアドレス
        password=pwd_context.hash("password1"),  # パスワードをハッシュ化
        type_id=1,
        occupation_id="1",
        overtime_id=10
    ),
    Usertable(
        user_name="山田花子",
        email="new_test2@example.com",  # 異なるメールアドレス
        password=pwd_context.hash("password2"),  # パスワードをハッシュ化
        type_id=2,
        occupation_id="2",
        overtime_id=20
    )
]

# データベースにテストデータを挿入する関数
def insert_test_data(session: Session, data):
    # 既存のデータを削除
    session.query(Usertable).delete()
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
