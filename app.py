import requests
import json
import pandas as pd
from datetime import datetime
import sqlite3
from openai import OpenAI
import os

today = datetime.today().strftime('%Y-%m-%d')

url = 'https://api.ouraring.com/v2/usercollection/daily_readiness' 
params={ 
    'start_date': today, 
    'end_date': today 
}
headers = { 
  'Authorization': 'Bearer YDSWVXKOZFL3BT4EV6KYXA2YVCXZA2IQ' 
}
response = requests.request('GET', url, headers=headers, params=params) 
print(response.text)

data = response.json()

# scoreを取得
score = data['data'][0]['score']

# scoreに基づいてscore_idを計算
if 0 <= score <= 25:
    score_id = 1
elif 26 <= score <= 50:
    score_id = 2
elif 51 <= score <= 75:
    score_id = 3
elif 76 <= score <= 100:
    score_id = 4
else:
    score_id = None  # 範囲外のスコアに対するエラーハンドリング

# scoreとscore_idを出力
print(f"Score: {score}")
print(f"Score ID: {score_id}")

# SQLiteデータベースに接続
conn = sqlite3.connect('heattech.db')
cursor = conn.cursor()

# 指定されたscore_idに一致するレコードを取得
query = "SELECT * FROM copingmaster WHERE score_id = ?"
cursor.execute(query, (score_id,))
record = cursor.fetchone()

# 結果を表示
if record:
    print(f"コーピングリスト： {record}")
else:
    print(f"No record found for score_id {score_id}")



api_key = 'API-KEY'

client = OpenAI(api_key=api_key)

chat_completion = client.chat.completions.create(
    messages=[
        {"role": "system", "content": "あなたは疲れているビジネスマンに休憩の方法をアドバイスする、経験豊富なアドバイザーです。働きすぎている人に警告を出す語調で話してください。"},
        {"role": "user", "content": f"{record[1]}の傾向がある人はどんな人か、教えて下さい。その後、{record[5]}を紹介してください。"}
    ],
    model="gpt-3.5-turbo",
)

print(chat_completion.choices[0].message)

# データベース接続を閉じる
conn.close()






