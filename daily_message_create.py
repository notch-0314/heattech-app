import requests
import json
import pandas as pd
from datetime import datetime
import sqlite3
from openai import OpenAI
import os
import fastapi

today = datetime.today().strftime('%Y-%m-%d')

url = 'https://api.ouraring.com/v2/usercollection/daily_readiness' 
params={ 
    'start_date': '2024-07-10', 
    'end_date': '2024-07-11' 
}
headers = { 
  'Authorization': 'Bearer api-key' 
}
response = requests.request('GET', url, headers=headers, params=params) 
print(response.text)

data = response.json()

# 前日スコアと当日スコアを取得
todays_score = data['data'][1]['score']
previous_days_score = data['data'][0]['score']

# scoreに基づいてscore_idを計算
if 0 <= todays_score <= 25:
    score_id = 1
elif 26 <= todays_score <= 50:
    score_id = 2
elif 51 <= todays_score <= 75:
    score_id = 3
elif 76 <= todays_score <= 100:
    score_id = 4
else:
    score_id = None  # 範囲外のスコアに対するエラーハンドリング

# scoreとscore_idを出力
print(f"Score: {todays_score}")
print(f"Score ID: {score_id}")

## コーピングマスタに照合
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




# データベース接続を閉じる
conn.close()

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
'''

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








