"use client";

import { useState } from 'react';
import Image from 'next/image';
import Link from 'next/link';

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

  const handleImageClick = () => {
    setShowModal(true);
  };

  const handleEvaluationClick = () => {
    setShowModal(false);
    setShowEvaluationModal(true);
  };

  const handleRadioChange = (e) => {
    setSelectedOption(e.target.value);
  };

  const handleEvaluate = () => {
    setShowEvaluationModal(false);
    setShowResultModal(true);
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
        <h1 className="text-lg font-bold">田中さんのコンディション</h1>

        <div className="w-1/3 bg-green-100 p-4 my-4">
          <p className="text-left text-xs font-bold">レコメンド</p>
        </div>

        <div className="relative w-full bg-gray-200 p-4 my-4">
          <p className="text-left">
            高ストレス状態が続いており、意識的に休息をとることが必要です。
            <br />
            性格傾向からブレインフォグや燃え尽き症候群となる可能性が高く、
            <br />
            パフォーマンスが低下するリスクがあります。
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

        <div className="w-full p-4 my-2 text-sm">
          <div className="flex">
            <div className="w-2/3 bg-gray-200 p-4">
              <p className="text-left">
                緊張状態が続いています。目を閉じて、長い呼吸を1~2分程度してみましょう。
              </p>
            </div>
            <div className="w-1/3 flex justify-center items-center">
              <div className="flex space-x-1">
                <div className="cursor-pointer" onClick={handleImageClick}>
                  <Image src="/action.png" alt="Action" width={60} height={60} />
                </div>
              </div>
            </div>
          </div>
        </div>
        <div className="w-full p-4 my-2 text-sm">
          <div className="flex">
            <div className="w-2/3 bg-gray-200 p-4">
              <p className="text-left">
                〇〇公園では、紫陽花が見ごろのようです。気分転換に散歩してみてはいかがでしょう。
              </p>
            </div>
            <div className="w-1/3 flex justify-center items-center">
              <div className="flex space-x-1">
                <div className="cursor-pointer" onClick={handleImageClick}>
                  <Image src="/action.png" alt="Action" width={60} height={60} />
                </div>
              </div>
            </div>
          </div>
        </div>
        <div className="w-full p-4 my-2 text-sm">
          <div className="flex">
            <div className="w-2/3 bg-gray-200 p-4">
              <p className="text-left">
                〇〇では、入浴＋サウナセットがXXXXで入れます。脳疲労が取れるので、あなたにお勧めです。
              </p>
            </div>
            <div className="w-1/3 flex justify-center items-center">
              <div className="flex space-x-1">
                <div className="cursor-pointer" onClick={handleImageClick}>
                  <Image src="/action.png" alt="Action" width={60} height={60} />
                </div>
              </div>
            </div>
          </div>
        </div>
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
              瞑想により心拍数が下がり、リラックス傾向が高まりました。
              先ほどより頭もすっきり冴えていることでしょう。
              定期的に休憩を取り、午後も頑張りましょう！
            </p>
          </div>
          <div className="flex space-x-8">
            <div className="bg-white bg-opacity-60 rounded-lg p-4 text-center">
              <p className="text-lg">最低心拍数</p>
              <p className="text-2xl font-bold">80bpm</p>
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
