from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import pytz

DATABASE_URL = "sqlite:///./heattech.db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 日本時間（JST）を取得する関数
def jst_now():
    return datetime.now(pytz.timezone('Asia/Tokyo'))

# テーブルの定義
class CopingMessage(Base):
    __tablename__ = "coping_message"

    coping_message_id = Column(Integer, primary_key=True, index=True)
    coping_message_text = Column(Text)
    satisfaction_score = Column(String)
    heart_rate_before = Column(Integer)
    heart_rate_after = Column(Integer)
    create_datetime = Column(String)
    update_datetime = Column(String)

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
