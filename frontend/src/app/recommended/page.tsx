"use client";

import { useState, useEffect } from 'react';
import Image from 'next/image';
import Link from 'next/link';
import { useRouter } from 'next/navigation';

export default function Recommended() {
  const [data, setData] = useState({
    mypage: { src: '/mypage.png', label: 'マイページ', link: '/mypage' },
    health: { src: '/health.png', label: 'コンディション', link: '/condition' },
    recommended: { src: '/recommended.png', label: 'レコメンド', link: '/recommended' },
  });

  const [showModal, setShowModal] = useState(false);
  const [showEvaluationModal, setShowEvaluationModal] = useState(false);
  const [showResultModal, setShowResultModal] = useState(false);
  const [selectedOption, setSelectedOption] = useState('');
  const [copingMessages, setCopingMessages] = useState([]);
  const [userName, setUserName] = useState(''); 
  const [assistantText, setAssistantText] = useState(''); // assistant_textを保存する状態
  const [completedActivities, setCompletedActivities] = useState([]); // 実施済みアクティビティを追跡
  const [heartRateBefore, setHeartRateBefore] = useState(null); // 心拍数（開始）
  const [heartRateAfter, setHeartRateAfter] = useState(null); // 心拍数（終了）
  const [evaluationMessage, setEvaluationMessage] = useState(''); // 評価メッセージ
  const router = useRouter();

  useEffect(() => {
    async function fetchData() {
      const token = localStorage.getItem('token');
      if (!token) {
        console.error("No token found");
        router.push('/login'); 
        return;
      }
      
      const baseURL = process.env.NEXT_PUBLIC_API_BASE_URL;
      const response = await fetch(`${baseURL}/coping_message`, {
          headers: {
              'Authorization': `Bearer ${token}`,
          },
      });


      if (response.ok) {
        const data = await response.json();
        console.log("Fetched data:", data); // デバッグ用
        setCopingMessages(data.coping_messages.slice(0, 3)); 
        setUserName(data.user_name); 
        setAssistantText(data.assistant_text); 
      } else if (response.status === 401) {
        console.error("Unauthorized, redirecting to login");
        router.push('/login'); 
      } else {
        console.error("Failed to fetch coping messages", response.status);
      }
    }

    fetchData();
  }, [router]);

  const handleImageClick = async (copingMessageId) => {
    setShowModal(true);

    try {
      const token = localStorage.getItem('token');
      const baseURL = process.env.NEXT_PUBLIC_API_BASE_URL;
      const response = await fetch(`${baseURL}/coping_start`, {
          method: 'POST',
          headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${token}`,
          },
          body: JSON.stringify({ coping_message_id: copingMessageId }),
      });


      if (response.ok) {
        const data = await response.json();
        setHeartRateBefore(data.heart_rate_before || 80); // デフォルト値80bpm
        setCompletedActivities([...completedActivities, copingMessageId]); // 実施済みアクティビティを追加
      } else {
        console.error("Failed to start coping", response.status);
        setHeartRateBefore(80); // 取得失敗時のデフォルト値
      }
    } catch (error) {
      console.error("An error occurred while starting coping", error);
      setHeartRateBefore(80); // エラー時のデフォルト値
    }
  };

  const handleEvaluationClick = () => {
    setShowModal(false);
    setShowEvaluationModal(true);
  };

  const handleRadioChange = (e) => {
    setSelectedOption(e.target.value);
  };

  const handleEvaluate = async () => {
    setShowEvaluationModal(false);
    setShowResultModal(true);

    try {
      const token = localStorage.getItem('token');
      const baseURL = process.env.NEXT_PUBLIC_API_BASE_URL;
      const response = await fetch(`${baseURL}/coping_finish`, {
          method: 'POST',
          headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${token}`,
          },
          body: JSON.stringify({ 
              coping_message_id: copingMessages[0]?.coping_message_id || 1, // 最初のメッセージを使うか、デフォルトIDを使用
              satisfaction_score: selectedOption,
          }),
      });


      if (response.ok) {
        const data = await response.json();
        setHeartRateAfter(data.latest_heart_rate || 80); // デフォルト値80bpm
        setEvaluationMessage(data.message || 'デフォルトのメッセージ');
      } else {
        console.error("Failed to finish coping", response.status);
        setHeartRateAfter(80); // 取得失敗時のデフォルト値
        setEvaluationMessage('デフォルトのメッセージ');
      }
    } catch (error) {
      console.error("An error occurred while finishing coping", error);
      setHeartRateAfter(80); // エラー時のデフォルト値
      setEvaluationMessage('デフォルトのメッセージ');
    }
  };

  const getFeelingText = () => {
    switch (selectedOption) {
      case 'much_better':
        return 'とても良好';
      case 'better':
        return 'やや良好';
      case 'same':
        return '普通';
      case 'worse':
        return 'やや不調';
      case 'much_worse':
        return 'とても不調';
      default:
        return '普通';
    }
  };

  return (
    <div className="flex flex-col items-center p-4 h-screen font-sans relative">
      <div className="w-full flex-grow overflow-auto pb-24">
        <h1 className="text-lg font-bold">{userName}さんのレコメンド</h1> 

        <div className="w-1/3 bg-green-100 p-4 my-4">
          <p className="text-left text-xs font-bold">レコメンド</p>
        </div>

        <div className="relative w-full bg-gray-200 p-4 my-4">
          <p className="text-left">
            {assistantText || '高ストレス状態が続いており、意識的に休息をとることが必要です。性格傾向からブレインフォグや燃え尽き症候群となる可能性が高く、パフォーマンスが低下するリスクがあります。'}
          </p>
        </div>

        <div className="flex justify-between items-center mb-4">
          <div className="w-1/3 bg-blue-100 p-4">
            <p className="text-left text-xs font-bold">アクティビティ</p>
          </div>
          <div className="w-2/3 text-xs ml-4">
            <p>実行するアクティビティのチェックボックスをクリックしてください。</p>
          </div>
        </div>

        {copingMessages.map((message, index) => (
          <div key={index} className="w-full p-4 my-2 text-sm">
            <div className="flex">
              <div className="w-2/3 bg-gray-200 p-4">
                <p className="text-left">{message.coping_message_text}</p>
              </div>
              <div className="w-1/3 flex justify-center items-center relative">
                <div className="flex space-x-1">
                  <div 
                    className="cursor-pointer relative" 
                    onClick={() => handleImageClick(message.coping_message_id)}
                  >
                    <Image 
                      src="/action.png" 
                      alt="Action" 
                      width={60} 
                      height={60} 
                      style={{
                        filter: completedActivities.includes(message.coping_message_id) ? 'grayscale(100%)' : 'grayscale(0%)',
                        opacity: completedActivities.includes(message.coping_message_id) ? 0.5 : 1
                      }} 
                    />
                    {completedActivities.includes(message.coping_message_id) && (
                      <p className="absolute -top-3 left-0 text-xs text-gray-500">実施済み</p>
                    )}
                  </div>
                </div>
              </div>
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
                </a>
              </Link>
              <span className="text-xs">{data[key].label}</span>
            </div>
          ))}
        </div>
      </div>

      {showModal && !showEvaluationModal && !showResultModal && (
        <div
          className="fixed inset-0 flex items-center justify-center z-50 bg-black bg-opacity-50"
          onClick={() => setShowModal(false)}
        >
          <div
            className="relative w-full max-w-screen-sm mx-auto flex flex-col items-center justify-center"
            onClick={(e) => e.stopPropagation()}
          >
            <div style={{ position: 'relative', width: '100%', height: '70vh' }}>
              <Image 
                src="/action_meditation.jpg" 
                alt="Meditation Action" 
                layout="fill"
                className="rounded-lg"
                style={{ filter: 'grayscale(80%)', objectFit: 'cover' }}
              />
              <div className="absolute inset-0 flex flex-col items-center justify-center text-gray-700 p-4">
                <h1 className="text-5xl font-bold mb-16">瞑想</h1>
                <p className="text-center text-xl mb-16">
                  目を閉じて、息を深く吸ってリラックスをしましょう。<br />
                  短時間でも心身が休まり、深い安らぎをもたらします。
                </p>
                <button
                  className="bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-700"
                  onClick={handleEvaluationClick}
                >
                  終了する
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {showEvaluationModal && !showResultModal && (
        <div
          className="fixed inset-0 flex items-center justify-center z-50 bg-black bg-opacity-50"
          onClick={() => setShowEvaluationModal(false)}
        >
          <div
            className="relative w-full max-w-screen-sm mx-auto flex flex-col items-center justify-center"
            onClick={(e) => e.stopPropagation()}
          >
            <div style={{ position: 'relative', width: '100%', height: '70vh' }}>
              <Image 
                src="/action_meditation.jpg" 
                alt="Meditation Action" 
                layout="fill"
                className="rounded-lg"
                style={{ filter: 'grayscale(80%)', objectFit: 'cover' }}
              />
              <div className="absolute inset-0 flex flex-col items-center justify-center text-gray-700 p-4">
                <h1 className="text-3xl font-bold mb-16">気分はどうですか？</h1>
                <div className="mb-8">
                  <label className="block text-lg mb-2">
                    <input
                      type="radio"
                      name="feeling"
                      value="much_better"
                      checked={selectedOption === 'much_better'}
                      onChange={handleRadioChange}
                      className="mr-2"
                    />
                    いつもよりずっと良い
                  </label>
                  <label className="block text-lg mb-2">
                    <input
                      type="radio"
                      name="feeling"
                      value="better"
                      checked={selectedOption === 'better'}
                      onChange={handleRadioChange}
                      className="mr-2"
                    />
                    いつもより良い
                  </label>
                  <label className="block text-lg mb-2">
                    <input
                      type="radio"
                      name="feeling"
                      value="same"
                      checked={selectedOption === 'same'}
                      onChange={handleRadioChange}
                      className="mr-2"
                    />
                    いつもと同じ
                  </label>
                  <label className="block text-lg mb-2">
                    <input
                      type="radio"
                      name="feeling"
                      value="worse"
                      checked={selectedOption === 'worse'}
                      onChange={handleRadioChange}
                      className="mr-2"
                    />
                    いつもより悪い
                  </label>
                  <label className="block text-lg mb-2">
                    <input
                      type="radio"
                      name="feeling"
                      value="much_worse"
                      checked={selectedOption === 'much_worse'}
                      onChange={handleRadioChange}
                      className="mr-2"
                    />
                    いつもよりずっと悪い
                  </label>
                </div>
                <button
                  className="bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-700"
                  onClick={handleEvaluate}
                >
                  評価する
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {showResultModal && (
        <div
          className="fixed inset-0 flex items-center justify-center z-50 bg-black bg-opacity-50"
          onClick={() => setShowResultModal(false)}
        >
          <div
            className="relative w-full max-w-screen-sm mx-auto flex flex-col items-center justify-center"
            onClick={(e) => e.stopPropagation()}
          >
            <div style={{ position: 'relative', width: '100%', height: '70vh' }}>
              <Image 
                src="/action_meditation.jpg" 
                alt="Meditation Action" 
                layout="fill"
                className="rounded-lg"
                style={{ filter: 'grayscale(80%)', objectFit: 'cover' }}
              />
              <div className="absolute inset-0 flex flex-col items-center justify-center text-gray-700 p-4 space-y-8">
                <div className="bg-white bg-opacity-60 rounded-lg p-4 mb-8">
                  <p className="text-center text-lg">
                    {evaluationMessage}
                  </p>
                </div>
                <div className="flex space-x-8">
                  <div className="bg-white bg-opacity-60 rounded-lg p-4 text-center">
                    <p className="text-lg">最低心拍数</p>
                    <p className="text-2xl font-bold">{heartRateAfter || 80}bpm</p>
                  </div>
                  <div className="bg-white bg-opacity-60 rounded-lg p-4 text-center">
                    <p className="text-lg">気分</p>
                    <p className="text-2xl font-bold">{getFeelingText()}</p>
                  </div>
                </div>
                <button
                  className="bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-700 mt-8"
                  onClick={() => setShowResultModal(false)}
                >
                  アクティビティを終了する
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
