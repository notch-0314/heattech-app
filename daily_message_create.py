import requests
from datetime import datetime, timedelta
from openai import OpenAI
import os
from models import CopingMaster, User, CopingMessage, DailyMessage
from sqlalchemy import and_, func
from sqlalchemy.orm import Session
from db.db_config import SessionLocal
from dotenv import load_dotenv
import random

# .envファイルから環境変数を読み込む
load_dotenv()

# 環境変数からAPIキーを取得
OURA_API_KEY_1 = os.getenv('OURA_API_KEY_1')
OURA_API_KEY_2 = os.getenv('OURA_API_KEY_2')
GPT_API_KEY = os.getenv('GPT_API_KEY')

# 日付に関する定義
yesterday_date = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')
today_date = datetime.today().strftime('%Y-%m-%d')
today = datetime.today().strftime('%Y-%m-%d')
current_day = datetime.today().weekday()  # 月曜日=0, 日曜日=6

# time_valuesを取得
if current_day in [0, 1, 2, 3, 4]:  # 平日
    time_values = (10, 60, 180)
else:  # 休日
    time_values = (60, 180, 200)

# SQLAlchemyのDB接続
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 指定したコーピングをコーピングマスタから取得する関数
def fetch_coping_master(db: Session, score_id: int, time_value: int):
    return db.query(CopingMaster).filter(
        CopingMaster.type_name == '焦燥',
        CopingMaster.score_id == score_id,
        CopingMaster.time == time_value
    ).all()

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

    # データからスコアを抽出
    scores = {entry['day']: entry['score'] for entry in data['data']}
    return scores.get(yesterday_date), scores.get(today_date)

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

# スコアに合わせてランダムにプロンプトを取得する関数
def get_assistant_content(score_id):
    if score_id == 1:
        messages = [
            "あなたの健康状態は非常に悪いです。このままでは仕事のパフォーマンスが落ち、最終的には重大な問題を引き起こす可能性があります。ご自身を大切にして、今すぐ休息を取ってください。",
            "今の健康状態は非常に悪いです。このままではあなたの仕事にも影響が出てしまいます。一度、全てを忘れて休息を取ってください。",
            "非常に疲れが溜まっています。このままでは健康に大きな影響が出ます。ご自身のために、今すぐ休んでください。"
        ]
    elif score_id == 2:
        messages = [
            "健康が少し悪化傾向にあります。今休息を取らなければ、さらに悪化し、重要な仕事に支障が出るかもしれません。あなたの努力は素晴らしいですが、早めに休息を心がけてください。",
            "健康状態が少し悪化しています。今のうちに休息を取らないと、仕事に支障をきたす恐れがあります。早めの休息をお願いします。",
            "最近、健康が悪化し始めています。今のうちに休息を取ることで、さらなる悪化を防げます。少しだけでも休んでください。"
        ]
    elif score_id == 3:
        messages = [
            "健康状態は通常です。この調子で健康を維持し、最高のパフォーマンスを発揮するために、適度な休息を取り入れてください。ご自身の健康が一番大切です。",
            "現在の健康状態は良好です。この調子を維持するために、適度な休息を忘れずに取りましょう。健康が何よりも大切です。",
            "あなたの健康状態は通常です。この調子で日々の疲れを取り除き、仕事のパフォーマンスを維持するために、適度な休息を取りましょう。"
        ]
    elif score_id == 4:
        messages = [
            "健康状態は良好です。この調子で健康を維持し、さらなる成功を収めるために、定期的な休息を続けてください！",
            "今の健康状態は非常に良いです。この状態を維持するために、適度な休息を続けてください！",
            "健康状態は非常に良好です。この調子で健康を保ち、さらなる成功を目指して休息を取り続けてください！"
        ]
    
    return random.choice(messages)

# 取得したtime_valueの数だけcoping_masterからコーピングレコードを取得する関数
def fetch_all_coping_lists(db: Session, score_id: int, time_values):
    coping_lists = []
    for time_value in time_values:
        result = fetch_coping_master(db, score_id, time_value)
        if result:
            random_record = random.choice(result)  # ランダムに1行を選択
            coping_lists.append(random_record)
    return coping_lists

# GPTを利用する関数
def generate_gpt_response(coping_lists):
    advice_lists = []
    client = OpenAI(api_key=GPT_API_KEY)
    for index, record in enumerate(coping_lists):
        try:
            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "あなたは疲れているビジネスマンに休憩の方法をアドバイスする、経験豊富なアドバイザーです。彼らは責任感が強く、休むことに対して罪悪感を感じる傾向があります。"},
                    {"role": "user", "content": "以下の休憩方法を50字以内で紹介してください。"},
                    {"role": "user", "content": f"{record.rest_type}"}
                ],
                model="gpt-4-turbo",
            )
            advice = chat_completion.choices[0].message.content.strip()
            advice_lists.append(advice)
            print(f"Advice for coping item {index + 1}: {advice}")

        except Exception as e:
            print(f"Error processing coping item {index + 1}: {e}")

    return advice_lists

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

# coping_messageを取り出す関数
def get_coping_results(db, user_id, today_date):
    return db.query(CopingMessage).filter(
        CopingMessage.user_id == user_id,
        func.date(CopingMessage.create_datetime) == today_date,
        CopingMessage.satisfaction_score.isnot(None)
    ).all()

# daily_messageを生成する関数
def generate_daily_message_text(coping_results, todays_score, yesterdays_score):
    if coping_results:
        if todays_score >= yesterdays_score:
            return '昨日より今日のほうがスコアが良い、または同じです。休息を取ったからですね。'
        else:
            return '昨日と比較してスコアは少し低下しています。休息を昨日よりも取るように心がけましょう。'
    elif todays_score is None:
        return '当日スコアがないため比較できません'
    else:
        if todays_score >= yesterdays_score:
            return '日より今日のほうがスコアが良い、または同じです。この調子を維持するために、余裕があれば休息を取りましょう。'
        else:
            return '昨日と比較してスコアは少し低下しています。休息が取れていないので、積極的に休息を取りましょう。'

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
        coping_lists = fetch_all_coping_lists(db, score_id, time_values)

        # GPTにアクセス
        advice_lists = generate_gpt_response(coping_lists)

        # advice_listごとに保存
        for advice_list in advice_lists:
            save_coping_message(db, user.user_id, advice_list)
            print(advice_list)
            print("-" * 50)

        # クエリの実行
        coping_results = get_coping_results(db, user.user_id, today_date)

        # 取得したコーピングメッセージの表示
        for coping in coping_results:
            print(f'当てはまるcoping_messageは{coping.coping_message_text, coping.satisfaction_score}')

        # daily_messageの生成
        daily_message_text = generate_daily_message_text(coping_results, todays_score, yesterdays_score)

        # daily_messagesテーブルにdaily_messageを格納
        save_daily_message(db, user.user_id, daily_message_text, yesterdays_score, todays_score)

    # セッションのクローズ
    db_gen.close()

if __name__ == "__main__":
    main()







