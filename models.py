from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./heattech.db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class CopingMessage(Base):
    __tablename__ = "coping_message"

    coping_message_id = Column(Integer, primary_key=True, index=True)
    coping_id = Column(Integer)
    coping_message_text = Column(Text)
    selected = Column(Integer)
    satisfaction_score = Column(String)
    heart_rate_before = Column(Integer)
    heart_rate_after = Column(Integer)
    create_datetime = Column(String)
    update_datetime = Column(String)

Base.metadata.create_all(bind=engine)
