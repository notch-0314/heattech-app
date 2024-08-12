"use client";

import React, { useState, useEffect } from 'react';
import Image from 'next/image';
import Link from 'next/link';
import { useRouter } from 'next/navigation';

export default function Recommended() {
  const [data, setData] = useState({
    mypage: { src: '/mypage.png', label: 'マイページ', link: '/mypage' },
    health: { src: '/health.png', label: 'コンディション', link: '/condition' },
    recommended: { src: '/recommended.png', label: 'レコメンド', link: '/recommended' },
  });

  const [userName, setUserName] = useState('');
  const [previousScore, setPreviousScore] = useState(0);
  const [todayScore, setTodayScore] = useState(0);
  const [previousCondition, setPreviousCondition] = useState('');
  const [todayCondition, setTodayCondition] = useState('');
  const [dailyMessageText, setDailyMessageText] = useState('');
  const router = useRouter();

  const [conditions, setConditions] = useState({
    安静時心拍数: { text: "", value: 0 },
    心拍変動バランス: { text: "", value: 0 },
    体表温: { text: "", value: 0 },
    回復指数: { text: "", value: 0 },
    睡眠: { text: "", value: 0 },
    睡眠バランス: { text: "", value: 0 },
    前日アクティビティ: { text: "", value: 0 },
    アクティビティバランス: { text: "", value: 0 },
  });

  useEffect(() => {
    async function fetchData() {
      const token = localStorage.getItem('token');
      if (!token) {
        console.error("No token found");
        router.push('/login'); // トークンがない場合はログインページにリダイレクト
        return;
      }

      const response = await fetch('http://127.0.0.1:8000/condition', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();

        // 取得できた部分だけを更新する
        setUserName(data.user_name);
        setPreviousScore(data.previous_days_score || previousScore);
        setTodayScore(data.todays_days_score || todayScore);
        setPreviousCondition(getConditionText(data.previous_days_score || previousScore));
        setTodayCondition(getConditionText(data.todays_days_score || todayScore));
        setDailyMessageText(data.daily_message_text || dailyMessageText);

        // conditionsの更新
        const updatedConditions = {
          安静時心拍数: { text: data.resting_heart_rate || conditions.安静時心拍数.text, value: data.resting_heart_rate || 0 },
          心拍変動バランス: { text: data.hrv_balance || conditions.心拍変動バランス.text, value: data.hrv_balance || 0 },
          体表温: { text: data.body_temperature || conditions.体表温.text, value: data.body_temperature || 0 },
          回復指数: { text: data.recovery_index || conditions.回復指数.text, value: data.recovery_index || 0 },
          睡眠: { text: data.previous_night || conditions.睡眠.text, value: data.previous_night || 0 },
          睡眠バランス: { text: data.sleep_balance || conditions.睡眠バランス.text, value: data.sleep_balance || 0 },
          前日アクティビティ: { text: data.previous_day_activity || conditions.前日アクティビティ.text, value: data.previous_day_activity || 0 },
          アクティビティバランス: { text: data.activity_balance || conditions.アクティビティバランス.text, value: data.activity_balance || 0 }
        };

        setConditions(updatedConditions);
      } else if (response.status === 401) {
        console.error("Unauthorized, redirecting to login");
        router.push('/login'); // 認証失敗時にログインページへリダイレクト
      } else {
        console.error("Failed to fetch condition data", response.status);
      }
    }

    fetchData();
  }, []);

  const getConditionText = (score) => {
    if (score >= 80) return '良好';
    if (score >= 50) return '適度';
    if (score >= 30) return '不調';
    return '注意';
  };

  const getColorForCondition = (conditionValue) => {
    if (conditionValue >= 80) return 'bg-blue-100';
    if (conditionValue >= 50) return 'bg-yellow-100';
    if (conditionValue >= 30) return 'bg-pink-300';
    return 'bg-red-300';
  };

  return (
    <div className="flex flex-col items-center p-4 h-screen font-sans">
      <div className="w-full flex-grow overflow-auto pb-24">
        <h1 className="text-lg font-bold">{userName}さんのコンディション</h1>

        <div className="w-full bg-green-100 p-4 my-4 rounded-lg">
          {dailyMessageText}
        </div>

        <h2 className="text-lg font-semibold mb-2">コンディションスコア</h2>
        <div className="w-full flex justify-between my-4">
          <div className="w-1/2 bg-gray-200 p-6 text-center mx-2">
            <p>Previous Score</p>
            <p className="my-2">
              <span className="text-4xl">{previousScore}</span>
              <span className="text-xl ml-2">{previousCondition}</span>
            </p>
          </div>
          <div className="w-1/2 bg-gray-200 p-6 text-center mx-2">
            <p>Today Score</p>
            <p className="my-2">
              <span className="text-4xl">{todayScore}</span>
              <span className="text-xl ml-2">{todayCondition}</span>
            </p>
          </div>
        </div>

        <h2 className="text-lg font-semibold mb-2">コンディショントリビューター</h2>

        {Object.entries(conditions).map(([key, condition]) => (
          <div className="mb-4" key={key}>
            <div className="flex justify-between">
              <p>{key}</p>
              <p>{condition.text}</p>
            </div>
            <div className="w-full h-2 bg-gray-300 rounded">
              <div className={`${getColorForCondition(condition.value)} h-2 rounded`} style={{ width: `${condition.value}%` }}></div>
            </div>
          </div>
        ))}
      </div>

      <div className="w-full border-t border-gray-300 pt-4 fixed bottom-0 bg-white">
        <div className="w-full flex justify-around mb-4">
          {Object.keys(data).map((key) => (
            <div key={key} className="text-center">
              <Link href={data[key].link} legacyBehavior>
                <a>
                  <div className="relative w-16 h-16 mb-2 cursor-pointer">
                    <Image src={data[key].src} alt={data[key].label} fill style={{ objectFit: 'cover' }} />
                  </div>
                  <span className="text-xs">{data[key].label}</span>
                </a>
              </Link>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
