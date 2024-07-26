// src/app/recommended/page.tsx
"use client";

import Image from 'next/image';
import Link from 'next/link';
import { useState } from 'react';

function getRandomCondition() {
  const conditions = [
    { text: "良好", color: "bg-blue-500", range: [80, 100] },
    { text: "適度", color: "bg-pink-500", range: [50, 79] },
    { text: "不調", color: "bg-yellow-500", range: [30, 49] },
    { text: "注意", color: "bg-red-500", range: [1, 29] },
  ];

  const condition = conditions[Math.floor(Math.random() * 2)]; // 良好と適度を多く
  const value = Math.floor(
    Math.random() * (condition.range[1] - condition.range[0] + 1) + condition.range[0]
  );

  return { text: condition.text, color: condition.color, value };
}

export default function Recommended() {
  const [data, setData] = useState({
    mypage: { src: '/mypage.png', label: 'マイページ', link: '/mypage' },
    health: { src: '/health.png', label: 'コンディション', link: '/condition' },
    recommended: { src: '/recommended.png', label: 'レコメンド', link: '/recommended' },
  });

  const conditions = {
    安静時心拍数: getRandomCondition(),
    心拍変動バランス: getRandomCondition(),
    体表温: getRandomCondition(),
    回復指数: getRandomCondition(),
    睡眠: getRandomCondition(),
    睡眠バランス: getRandomCondition(),
    睡眠規則性: getRandomCondition(),
    前日アクティビティ: getRandomCondition(),
    アクティビティバランス: getRandomCondition(),
  };

  return (
    <div className="flex flex-col items-center p-4 h-screen font-sans">
      <div className="w-full flex-grow overflow-auto pb-24">
        {/* ①左上に名前とコンディション文言 */}
        <h1 className="text-lg font-bold">田中さんのコンディション</h1>

        {/* ①角丸四角形 */}
        <div className="w-full bg-green-100 p-4 my-4 rounded-lg">
          昨日は瞑想や散歩などのアクティビティを頑張りましたね。コンディションスコアも心拍バランスを中心に良好です。この調子で頑張りましょう。
        </div>

        {/* ②コンディションスコア */}
        <h2 className="text-lg font-semibold mb-2">コンディションスコア</h2>
        <div className="w-full flex justify-between my-4">
          <div className="w-1/2 bg-gray-200 p-6 text-center mx-2">
            <p>Previous Score</p>
            <p className="my-2">
              <span className="text-4xl">50</span>
              <span className="text-xl ml-2">適度</span>
            </p>
          </div>
          <div className="w-1/2 bg-gray-200 p-6 text-center mx-2">
            <p>Today Score</p>
            <p className="my-2">
              <span className="text-4xl">84</span>
              <span className="text-xl ml-2">良好</span>
            </p>
          </div>
        </div>

        {/* ③コンディショントリビューター */}
        <h2 className="text-lg font-semibold mb-2">コンディショントリビューター</h2>

        {Object.entries(conditions).map(([key, condition]) => (
          <div className="mb-4" key={key}>
            <div className="flex justify-between">
              <p>{key}</p>
              <p>{condition.text}</p>
            </div>
            <div className="w-full h-2 bg-gray-300 rounded">
              <div className={`${condition.color} h-2 rounded`} style={{ width: `${condition.value}%` }}></div>
            </div>
          </div>
        ))}
      </div>

      {/* 下部の画像アイコン */}
      <div className="w-full border-t border-gray-300 pt-4 fixed bottom-0 bg-white">
        <div className="w-full flex justify-around mb-4">
          {Object.keys(data).map((key) => (
            <div key={key} className="text-center">
              <Link href={data[key].link} legacyBehavior>
                <a>
                  <div className="relative w-16 h-16 mb-2 cursor-pointer">
                    <Image src={data[key].src} alt={data[key].label} fill objectFit="cover" />
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
