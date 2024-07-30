// src/app/page.js
import Image from 'next/image';

export default function Condition() {
  return (
    <div className="flex flex-col items-center justify-end h-screen p-4">
      <div className="w-full border-t border-gray-300 mb-4"></div>
      <div className="w-full flex justify-around mb-4">
        <div className="text-center">
          <div className="relative w-16 h-16 mb-2">
            <Image src="/mypage.png" alt="My Page" layout="fill" objectFit="cover" />
          </div>
          <span className="text-xs">マイページ</span>
        </div>
        <div className="text-center">
          <div className="relative w-16 h-16 mb-2">
            <Image src="/health.png" alt="Health" layout="fill" objectFit="cover" />
          </div>
          <span className="text-xs">コンディション</span>
        </div>
        <div className="text-center">
          <div className="relative w-16 h-16 mb-2">
            <Image src="/recommended.png" alt="Recommended" layout="fill" objectFit="cover" />
          </div>
          <span className="text-xs">レコメンド</span>
        </div>
      </div>
    </div>
  );
}
