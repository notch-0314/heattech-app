import requests
import json
import pandas as pd
from datetime import datetime, timedelta
import sqlite3
from openai import OpenAI
import os
from models import CopingMaster, User, CopingMessage, DailyMessage
from sqlalchemy import and_, func
from sqlalchemy.orm import Session
from db.db_config import SessionLocal
from dotenv import load_dotenv

# .envファイルから環境変数を読み込む
load_dotenv()

# 環境変数からAPIキーを取得
OURA_API_KEY_1 = os.getenv('OURA_API_KEY_1')
OURA_API_KEY_2 = os.getenv('OURA_API_KEY_2')
GPT_API_KEY = os.getenv('GPT_API_KEY')

# 日付に関する定義
today = datetime.today()
yesterday = today - timedelta(days=1)
yesterday_date = yesterday.strftime('%Y-%m-%d')
today_date = today.strftime('%Y-%m-%d')

# SQLAlchemyのDB接続
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 指定したコーピングをコーピングマスタから取得する関数
def fetch_coping_master(db: Session, score_id: int):
    result = db.query(CopingMaster).filter(CopingMaster.type_name == '焦燥', CopingMaster.score_id == score_id, CopingMaster.time == 180).all()
    return result

# OuraAPIから昨日と今日のスコアを取得する関数
def fetch_daily_readiness(api_key: str):

    url = 'https://api.ouraring.com/v2/usercollection/daily_readiness'
    params = {
        'start_date': yesterday_date,
        'end_date': today_date
    }
    headers = {
        'Authorization': f'Bearer {api_key}'
    }
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code != 200:
        print(f"Failed to fetch data from API, status code: {response.status_code}")
        return None, None
    
    data = response.json()
    
    if not data['data']:
        print("No data found for today")
        return None, None
    
    print(json.dumps(data, indent=2))  # レスポンス全体を出力して構造を確認
    
    # データからスコアを抽出
    scores = {entry['day']: entry['score'] for entry in data['data']}
    
    yesterdays_score = scores.get(yesterday_date)
    todays_score = scores.get(today_date)
    print(yesterdays_score, todays_score)

    return yesterdays_score, todays_score

# ユーザーによってOuraAPIキーを変える関数
def select_api_key(user):
    if user.oura_id == 1:
        return OURA_API_KEY_1
    elif user.oura_id == 2:
        return OURA_API_KEY_2
    else:
        print(f"Invalid user type for user {user.user_name}")
        return None

# 今日のスコアからscore_idを取得する関数
def calculate_score_id(todays_score):
    if 0 <= todays_score <= 59:
        return 1
    elif 60 <= todays_score <= 69:
        return 2
    elif 70 <= todays_score <= 84:
        return 3
    elif 85 <= todays_score <= 100:
        return 4
    else:
        return None

# GPTを利用する関数
def generate_gpt_response(coping_how_to_rest):
    client = OpenAI(api_key=GPT_API_KEY)

    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "あなたは疲れているビジネスマンに休憩の方法をアドバイスする、経験豊富なアドバイザーです。働きすぎている人に警告を出す語調で話してください。"},
            {"role": "user", "content": f" {coping_how_to_rest}を紹介してください。"}
        ],
        model="gpt-3.5-turbo",
    )
    return chat_completion.choices[0].message.content

# coping_messageを保存する関数
def save_coping_message(db, user_id, message_text):
    new_coping_message = CopingMessage(
        user_id=user_id,
        coping_message_text=message_text,
        satisfaction_score="とても良い",
        heart_rate_before=0,
        heart_rate_after=0
    )
    db.add(new_coping_message)
    db.commit()

# daily_messageを保存する関数
def save_daily_message(db, user_id, daily_message_text, yesterdays_score, todays_score):
    new_daily_message = DailyMessage(
        user_id=user_id,
        daily_message_text=daily_message_text,
        previous_days_score=yesterdays_score,
        todays_days_score=todays_score
    )
    db.add(new_daily_message)
    db.commit()

def main():

    # データベースセッションの作成
    db_gen = get_db()
    db = next(db_gen)

    # すべてのユーザーを取得
    users = db.query(User).all()

    for user in users:
        # APIキーの選択
        api_key = select_api_key(user)
        if api_key is None:
            continue

        # APIからスコアを取得
        yesterdays_score, todays_score = fetch_daily_readiness(api_key)
        if todays_score is None:
            continue

        # スコアIDの計算
        score_id = calculate_score_id(todays_score)
        if score_id is None:
            print(f"{user.user_name}のスコアIDはありません")
            continue

        # scoreとscore_idを出力
        print(f"User: {user.user_name}")
        print(f"Score: {todays_score}")
        print(f"Score ID: {score_id}")

        # コーピングマスタに照合
        result = fetch_coping_master(db, score_id)

        # 結果を出力し、GPT応答生成と保存
        for coping in result:
            print(f"Coping Type: {coping.type_name}, Rest Type: {coping.rest_type}, How to Rest: {coping.how_to_rest}")
            message_text = generate_gpt_response(coping.how_to_rest)
            save_coping_message(db, user.user_id, message_text)
            print(message_text)
            print("-" * 50)
        
        # クエリの実行
        coping_results = db.query(CopingMessage).filter(
            and_(
                CopingMessage.user_id == user.user_id,
                func.date(CopingMessage.create_datetime) == today_date,
                CopingMessage.satisfaction_score.isnot(None)
            )
        ).all()

        for coping in coping_results:
            print(f'当てはまるcoping_messageは{coping.coping_message_text, coping.satisfaction_score}')

        if coping_results:
            if todays_score > yesterdays_score:
                daily_message_text = '昨日より今日のほうがスコアが良いです。休息を取ったからですね。'
            else:
                daily_message_text = '昨日とスコアは同じか少し低下しています。休息を昨日よりも取るように心がけましょう。'
        elif todays_score is None:
                daily_message_text = '当日スコアがないため比較できません'
        else:
            if todays_score > yesterdays_score:
                daily_message_text = '昨日より今日のほうがスコアが良いです。この調子を維持するために、余裕があれば休息を取りましょう。'
            else:
                daily_message_text = '昨日とスコアは同じか少し低下しています。休息が取れていないので、積極的に休息を取りましょう。'
        
        # daily_messagesテーブルにメッセージを格納
        save_daily_message(db, user.user_id, daily_message_text, yesterdays_score, todays_score)


    # セッションのクローズ
    db_gen.close()

if __name__ == "__main__":
    main()








