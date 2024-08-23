"use client";

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import axios from 'axios';

const LoginPage: React.FC = () => {
    const [username, setUsername] = useState<string>('');
    const [password, setPassword] = useState<string>('');
    const [error, setError] = useState<string | null>(null);
    const router = useRouter();

    const handleLogin = async (e: React.FormEvent) => {
        e.preventDefault();
        setError(null);  // エラーメッセージをリセット
        try {
            const params = new URLSearchParams();
            params.append('username', username);
            params.append('password', password);

            const baseURL = process.env.NEXT_PUBLIC_API_BASE_URL;
            const response = await axios.post(`${baseURL}/token`, params, {
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
            });

            if (response.status === 200) {
                const { access_token } = response.data;
                localStorage.setItem('token', access_token);
                router.push('/condition');
            }
        } catch (err) {
            if (axios.isAxiosError(err)) {
                // サーバーからのエラーメッセージがあればそれを表示、なければデフォルトメッセージを表示
                if (err.response) {
                    const status = err.response.status;
                    if (status === 401) {
                        setError('ユーザー名またはパスワードが正しくありません。');
                    } else if (status >= 500) {
                        setError('サーバーエラーが発生しました。時間をおいて再度お試しください。');
                    } else {
                        setError(err.response.data.detail || 'ログインに失敗しました。');
                    }
                } else {
                    setError('サーバーに接続できませんでした。ネットワークの状態を確認してください。');
                }
            } else {
                setError('予期しないエラーが発生しました。');
            }
        }
    };

    return (
        <div className="flex justify-center items-center h-screen">
            <form onSubmit={handleLogin} className="w-full max-w-sm bg-white p-6 rounded shadow-md">
                <h2 className="text-2xl font-bold text-center mb-4">ログイン</h2>
                {error && <p className="text-red-500 text-center">{error}</p>}
                <div className="mb-4">
                    <label htmlFor="username" className="block text-sm font-medium text-gray-700">
                        ユーザー名
                    </label>
                    <input
                        type="text"
                        id="username"
                        className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        required
                    />
                </div>
                <div className="mb-6">
                    <label htmlFor="password" className="block text-sm font-medium text-gray-700">
                        パスワード
                    </label>
                    <input
                        type="password"
                        id="password"
                        className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        required
                    />
                </div>
                <button
                    type="submit"
                    className="w-full py-2 px-4 bg-blue-500 text-white font-semibold rounded-md hover:bg-blue-600"
                >
                    ログイン
                </button>
            </form>
        </div>
    );
};

export default LoginPage;
