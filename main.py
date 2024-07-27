import requests
import json
import pandas as pd
from datetime import datetime, timedelta
import sqlite3
from openai import OpenAI
import os
from fastapi import FastAPI, HTTPException, Request, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from models import SessionLocal
from typing import List
import models

#以下、ログインに必要な機能をインポート
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from jose import JWTError, jwt
from schemas import Token, User, UserInDB
from typing import Optional
import pytz

app = FastAPI()

# 指定した日付のコーピングメッセージを取得する関数
def fetch_coping_message(db: Session):
    sql = text("SELECT * FROM coping_message WHERE create_datetime LIKE '2024-07-10%'")
    result = db.execute(sql).fetchall()
    return [dict(row._mapping) for row in result]

# 最新の心拍数を取得する関数
def read_heart_rate():
    url = 'https://api.ouraring.com/v2/usercollection/heartrate'
    params = {}
    headers = {
        'Authorization': 'Bearer YDSWVXKOZFL3BT4EV6KYXA2YVCXZA2IQ'
    }
    response = requests.request('GET', url, headers=headers, params=params)
    data = response.json()
    latest_bpm = data['data'][-1]['bpm'] if 'data' in data and len(data['data']) > 0 else None
    print(latest_bpm)
    return(latest_bpm)

# 心拍数をheart_rate_beforeに登録する関数
def update_heart_rate_before(db: Session, coping_message_id: int, heart_rate_before: int):
    sql = text("UPDATE coping_message SET heart_rate_before = :heart_rate_before WHERE coping_message_id = :coping_message_id")
    db.execute(sql, {'heart_rate_before': heart_rate_before, 'coping_message_id': coping_message_id})
    db.commit()

# 満足度を登録する関数
def update_satisfaction_score(db: Session, coping_message_id: int, satisfaction_score: int):
    sql = text("UPDATE coping_message SET satisfaction_score = :satisfaction_score WHERE coping_message_id = :coping_message_id")
    db.execute(sql, {'satisfaction_score': satisfaction_score, 'coping_message_id': coping_message_id})
    db.commit()

# 心拍数をheart_rate_afterに登録する関数
def update_heart_rate_after(db: Session, coping_message_id: int, heart_rate_after: int):
    sql = text("UPDATE coping_message SET heart_rate_after = :heart_rate_after WHERE coping_message_id = :coping_message_id")
    db.execute(sql, {'heart_rate_after': heart_rate_after, 'coping_message_id': coping_message_id})
    db.commit()

# 特定のcoping_message_idのheart_rate_beforeを取得する関数
def get_heart_rate_before(db: Session, coping_message_id: int):
    sql = text("SELECT * FROM coping_message WHERE coping_message_id = :coping_message_id")
    result = db.execute(sql, {'coping_message_id': coping_message_id}).fetchone()
    if result:
        result_dict = dict(result._mapping)
        print(f'結果は{result_dict}')
        return(result_dict["heart_rate_before"])
    else:
        raise HTTPException(status_code=404, detail="Coping message not found")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# コーピングメッセージ取得API
@app.get('/coping_message')
async def get_coping_message(db: Session = Depends(get_db)):
    messages = fetch_coping_message(db)
    return messages

# コーピング実施前の心拍数取得API
@app.post('/coping_start')
async def coping_start(db: Session = Depends(get_db)):
    latest_heart_rate = read_heart_rate()
    if latest_heart_rate is None:
        raise HTTPException(status_code=404, detail='心拍数が見つかりません')
    coping_message_id = 1
    update_heart_rate_before(db, coping_message_id, latest_heart_rate)
    return{"message": "心拍数を取得しました", "heart_rate_before": latest_heart_rate}

#コーピング実施後の満足度登録/心拍数取得/メッセージ表示API
@app.post('/coping_finish')
async def coping_finish(db: Session = Depends(get_db)):
    # coping_message_idとsatisfaction_scoreを代入（フロントから取得）
    coping_message_id = 1
    satisfaction_score = 'とても良好'
    # satisfaction_scoreを登録
    update_satisfaction_score(db, coping_message_id, satisfaction_score)
    latest_heart_rate = read_heart_rate()
    if latest_heart_rate is None:
        raise HTTPException(status_code=404, detail='心拍数が見つかりません')
    update_heart_rate_after(db, coping_message_id, latest_heart_rate)
    heart_rate_before = get_heart_rate_before(db, coping_message_id)
    if latest_heart_rate < heart_rate_before:
        message = '休息により心拍数が下がり、リラックス傾向が高まりました。この調子で、定期的に休憩を取りましょう！'
    else:
        message = '休息前と比べて、心拍数が変わっていない、または少し心拍数が上がっているようです。休息が十分でない可能性があるので、他の休息も取り入れてみると良いかもしれません。'

    return {
        'message': message,
        'heart_rate_before': heart_rate_before,
        'latest_heart_rate': latest_heart_rate,
        'satisfaction_score': satisfaction_score
    }

#以下ログインのための各種API作成
# シークレットキーの設定
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# パスワードのハッシュ化のための設定
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2の設定
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# ユーザーの認証
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[datetime] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# ユーザーを取得する関数
def get_user(db, username: str):
    return db.query(models.Usertable).filter(models.Usertable.user_name == username).first()

# ユーザーの認証
def authenticate_user(db, username: str, password: str):
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user

# トークンのデコード
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = get_user(db, username=username)
    if user is None:
        raise credentials_exception
    return user

# ログインAPI
@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.user_name}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# ユーザーの登録API
@app.post("/register")
async def register_user(user: User, db: Session = Depends(get_db)):
    db_user = models.Usertable(
        user_name=user.user_name,
        email=user.email,
        password=get_password_hash(user.password),
        type_id=0,  # 仮の値
        occupation_id="unknown",  # 仮の値
        overtime_id=0,  # 仮の値
        create_datetime=datetime.now(pytz.timezone('Asia/Tokyo')),
        update_datetime=datetime.now(pytz.timezone('Asia/Tokyo'))
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user