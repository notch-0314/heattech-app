from sqlalchemy import Column, Integer, String, Text, DateTime
from db.db_config import Base
import datetime
import pytz

# 日本時間取得
def jst_now():
    return datetime.now(pytz.timezone('Asia/Tokyo'))

# テーブルの定義
class CopingMessage(Base):
    __tablename__ = "coping_messages"

    coping_message_id = Column(Integer, primary_key=True, index=True)
    coping_message_text = Column(Text)
    satisfaction_score = Column(String)
    heart_rate_before = Column(Integer)
    heart_rate_after = Column(Integer)
    create_datetime = Column(DateTime, default=jst_now)
    update_datetime = Column(DateTime, default=jst_now, onupdate=jst_now)

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    user_name = Column(String(225), unique=True, index=True)
    email = Column(String(225), unique=True, index=True)
    password = Column(String(225))
    type_id = Column(Integer)
    occupation_id = Column(String(225))
    overtime_id = Column(Integer)
    create_datetime = Column(DateTime, default=jst_now)
    update_datetime = Column(DateTime, default=jst_now, onupdate=jst_now)
