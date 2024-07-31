from sqlalchemy import Column, Integer, String, Text
from db.db_config import Base

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
