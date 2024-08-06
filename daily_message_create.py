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

# APIリクエストを実行する関数
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

def main():

    # データベースセッションの作成
    db_gen = get_db()
    db = next(db_gen)

    # すべてのユーザーを取得
    users = db.query(User).all()

    for user in users:
        # ユーザーのuser_typeに基づいてAPIキーを選択
        if user.oura_id == 1:
            api_key = OURA_API_KEY_1
        elif user.oura_id == 2:
            api_key = OURA_API_KEY_2
        else:
            print(f"Invalid user type for user {user.user_name}")
            continue

        # APIからスコアを取得
        yesterdays_score, todays_score = fetch_daily_readiness(api_key)
        if todays_score is None:
            continue

        # scoreに基づいてscore_idを計算
        if 0 <= todays_score <= 59:
            score_id = 1
        elif 60 <= todays_score <= 69:
            score_id = 2
        elif 70 <= todays_score <= 84:
            score_id = 3
        elif 85 <= todays_score <= 100:
            score_id = 4
        else:
            print(f"Invalid score range for user {user.user_name}")
            continue

        # scoreとscore_idを出力
        print(f"User: {user.user_name}")
        print(f"Score: {todays_score}")
        print(f"Score ID: {score_id}")

        # コーピングマスタに照合
        result = fetch_coping_master(db, score_id)

        # 結果を出力
        for coping in result:
            print(f"Coping Type: {coping.type_name}, Rest Type: {coping.rest_type}, How to Rest: {coping.how_to_rest}")

            api_key = GPT_API_KEY

            client = OpenAI(api_key=api_key)

            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "あなたは疲れているビジネスマンに休憩の方法をアドバイスする、経験豊富なアドバイザーです。働きすぎている人に警告を出す語調で話してください。"},
                    {"role": "user", "content": f" {coping.how_to_rest}を紹介してください。"}
                ],
                model="gpt-3.5-turbo",
            )
            # GPTの応答を取得
            message_text = chat_completion.choices[0].message.content

            # CopingMessageインスタンスを作成してデータベースに保存
            new_coping_message = CopingMessage(
                user_id=user.user_id,
                coping_message_text=message_text,
                satisfaction_score="とても良い",
                heart_rate_before=0,
                heart_rate_after=0
            )

            db.add(new_coping_message)
            db.commit()

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
        # CopingMessageインスタンスを作成してデータベースに保存
        new_daily_message = DailyMessage(
            user_id=user.user_id,
            daily_message_text=daily_message_text,
            previous_days_score=yesterdays_score,
            todays_days_score=todays_score
        )

        db.add(new_daily_message)
        db.commit()


    # セッションのクローズ
    db_gen.close()

if __name__ == "__main__":
    main()








