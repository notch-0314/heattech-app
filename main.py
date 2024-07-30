import requests
import json
import pandas as pd
from datetime import datetime
import sqlite3
from openai import OpenAI
import os
from fastapi import FastAPI, HTTPException, Request, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from models import SessionLocal
from typing import List
import models


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
    print(data)
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
    return{
            "message": "心拍数を取得しました",
            "heart_rate_before": latest_heart_rate
        }

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