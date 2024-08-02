import requests
import json
import pandas as pd
from datetime import datetime
import sqlite3
from openai import OpenAI
import os
from models import CopingMaster, User, CopingMessage
from sqlalchemy.orm import Session
from db.db_config import SessionLocal
from dotenv import load_dotenv

# .envファイルから環境変数を読み込む
load_dotenv()

# 環境変数からAPIキーを取得
OURA_API_KEY_1 = os.getenv('OURA_API_KEY_1')
OURA_API_KEY_2 = os.getenv('OURA_API_KEY_2')
GPT_API_KEY = os.getenv('GPT_API_KEY')


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
    today = datetime.today().strftime('%Y-%m-%d')
    url = 'https://api.ouraring.com/v2/usercollection/daily_readiness'
    params = {
        'start_date': today,
        'end_date': today
    }
    headers = {
        'Authorization': f'Bearer {api_key}'
    }
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code != 200:
        print(f"Failed to fetch data from API, status code: {response.status_code}")
        return None
    
    data = response.json()
    
    if not data['data']:
        print("No data found for today")
        return None
    
    return data['data'][0]['score']


def main():

    # データベースセッションの作成
    db_gen = get_db()
    db = next(db_gen)

    # すべてのユーザーを取得
    users = db.query(User).all()

    for user in users:
        # ユーザーのuser_typeに基づいてAPIキーを選択
        if user.type_id == 1:
            api_key = OURA_API_KEY_1
        elif user.type_id == 2:
            api_key = OURA_API_KEY_2
        else:
            print(f"Invalid user type for user {user.user_name}")
            continue

        # APIからスコアを取得
        todays_score = fetch_daily_readiness(api_key)
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

            print('ここまでは来てる？')

            # GPTの応答を取得
            message_text = chat_completion.choices[0].message.content

            # CopingMessageインスタンスを作成してデータベースに保存
            new_coping_message = CopingMessage(
                coping_message_text=message_text,
                satisfaction_score="",
                heart_rate_before=0,
                heart_rate_after=0
            )

            db.add(new_coping_message)
            db.commit()

            print(message_text)
            print("-" * 50)

    # セッションのクローズ
    db_gen.close()

if __name__ == "__main__":
    main()

    '''
    ## GPTにコーピングリストを渡して文章を生成（GPTを稼働させないためコメントアウト）
    api_key = 'api-key'

    client = OpenAI(api_key=api_key)

    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "あなたは疲れているビジネスマンに休憩の方法をアドバイスする、経験豊富なアドバイザーです。働きすぎている人に警告を出す語調で話してください。"},
            {"role": "user", "content": f"{record[1]}の傾向がある人はどんな人か、教えて下さい。その後、{record[5]}を紹介してください。"}
        ],
        model="gpt-3.5-turbo",
    )

    print(chat_completion.choices[0].message)
    

    ## デイリーメッセージを作成
    # SQLiteデータベースに接続
    conn = sqlite3.connect('heattech.db')
    cursor = conn.cursor()

    # 指定されたscore_idに一致するレコードを取得
    query = "SELECT * FROM coping_message WHERE create_datetime LIKE '%2024-07-10%';"
    cursor.execute(query)
    rows = cursor.fetchall()

    # 結果を表示
    for row in rows:
        print(row)

    # データベース接続を閉じる
    conn.close()

    # 4カラム目に「1」が含まれているか、前日比のスコアで文章を出し分け
    if any(row[3] == 1 for row in rows) and todays_score - previous_days_score > 0:
        daily_message = '昨日より今日のほうがスコアが良いです。休息を取ったからですね。'
    elif any(row[3] == 1 for row in rows) and todays_score - previous_days_score <= 0:
        daily_message = '昨日とスコアは同じか少し低下しています。休息を昨日よりも取るように心がけましょう。'
    elif all(row[3] != 1 for row in rows) and todays_score - previous_days_score <= 0:
        daily_message = '昨日とスコアは同じか少し低下しています。休息が取れていないので、積極的に休息を取りましょう。'
    else:
        daily_message = '昨日より今日のほうがスコアが良いです。この調子を維持するために、余裕があれば休息を取りましょう。'

    # selectedが「1」になっている行のcoping_messageを取得
    coping_message_with_1 = [row[2] for row in rows if row[3] == 1]

    # selectedが「0」になっている行のcoping_messageを取得
    coping_message_with_0 = [row[2] for row in rows if row[3] == 0]


    print(daily_message)
    print(f'当日スコアは{todays_score}')
    print(f'前日スコアは{previous_days_score}')
    print(f'やったコーピングは{coping_message_with_1}です')
    print(f'やらなかったコーピングは{coping_message_with_0}です')
'''








