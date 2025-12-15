'use client';

import { useState } from 'react';

const BACKEND_URL = 'https://web-production-dbb4d.up.railway.app';

export default function Home() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleAppleLogin = async () => {
    setLoading(true);
    setError('');
    
    try {
      // Запрашиваем URL для авторизации у backend
      const response = await fetch(`${BACKEND_URL}/auth/apple/login`);
      const data = await response.json();
      
      if (data.auth_url) {
        // Редиректим пользователя на страницу авторизации Apple
        window.location.href = data.auth_url;
      } else {
        setError('Не удалось получить URL авторизации');
        setLoading(false);
      }
    } catch (err) {
      setError('Ошибка подключения к серверу. Убедитесь что backend запущен.');
      setLoading(false);
      console.error('Ошибка:', err);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-black">
      <main className="flex w-full max-w-md flex-col items-center gap-8 rounded-2xl bg-white p-12 shadow-2xl dark:bg-gray-800">
        
        {/* Заголовок */}
        <div className="text-center">
          <h1 className="mb-2 text-4xl font-bold text-gray-900 dark:text-white">
            Apple OAuth2
          </h1>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Референсная реализация Sign in with Apple
          </p>
        </div>

        {/* Иконка Apple */}
        <div className="flex h-24 w-24 items-center justify-center rounded-full bg-black dark:bg-white">
          <svg
            className="h-16 w-16 text-white dark:text-black"
            fill="currentColor"
            viewBox="0 0 24 24"
          >
            <path d="M17.05 20.28c-.98.95-2.05.8-3.08.35-1.09-.46-2.09-.48-3.24 0-1.44.62-2.2.44-3.06-.35C2.79 15.25 3.51 7.59 9.05 7.31c1.35.07 2.29.74 3.08.8 1.18-.24 2.31-.93 3.57-.84 1.51.12 2.65.72 3.4 1.8-3.12 1.87-2.38 5.98.48 7.13-.57 1.5-1.31 2.99-2.54 4.09l.01-.01zM12.03 7.25c-.15-2.23 1.66-4.07 3.74-4.25.29 2.58-2.34 4.5-3.74 4.25z" />
          </svg>
        </div>

        {/* Описание */}
        <div className="w-full space-y-3 text-center text-sm text-gray-600 dark:text-gray-400">
          <p>
            Нажмите кнопку ниже для авторизации через Apple ID
          </p>
          <div className="rounded-lg bg-blue-50 p-3 text-left dark:bg-blue-900/20">
            <p className="text-xs font-semibold text-blue-900 dark:text-blue-300">
              ⚠️ Перед использованием:
            </p>
            <ul className="mt-1 list-inside list-disc text-xs text-blue-800 dark:text-blue-400">
              <li>Заполните константы в <code className="font-mono">backend/config.py</code></li>
              <li>Запустите backend: <code className="font-mono">python backend/main.py</code></li>
              <li>Инструкция в <code className="font-mono">APPLE_SETUP.md</code></li>
            </ul>
          </div>
        </div>

        {/* Ошибка */}
        {error && (
          <div className="w-full rounded-lg bg-red-50 p-4 text-sm text-red-800 dark:bg-red-900/20 dark:text-red-300">
            {error}
          </div>
        )}

        {/* Кнопка Sign in with Apple */}
        <button
          onClick={handleAppleLogin}
          disabled={loading}
          className="flex w-full items-center justify-center gap-3 rounded-lg bg-black px-6 py-4 font-semibold text-white transition-all hover:bg-gray-800 disabled:cursor-not-allowed disabled:opacity-50 dark:bg-white dark:text-black dark:hover:bg-gray-200"
        >
          {loading ? (
            <>
              <svg
                className="h-5 w-5 animate-spin"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                ></circle>
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                ></path>
              </svg>
              Загрузка...
            </>
          ) : (
            <>
              <svg
                className="h-5 w-5"
                fill="currentColor"
                viewBox="0 0 24 24"
              >
                <path d="M17.05 20.28c-.98.95-2.05.8-3.08.35-1.09-.46-2.09-.48-3.24 0-1.44.62-2.2.44-3.06-.35C2.79 15.25 3.51 7.59 9.05 7.31c1.35.07 2.29.74 3.08.8 1.18-.24 2.31-.93 3.57-.84 1.51.12 2.65.72 3.4 1.8-3.12 1.87-2.38 5.98.48 7.13-.57 1.5-1.31 2.99-2.54 4.09l.01-.01zM12.03 7.25c-.15-2.23 1.66-4.07 3.74-4.25.29 2.58-2.34 4.5-3.74 4.25z" />
              </svg>
              Sign in with Apple
            </>
          )}
        </button>

        {/* Дополнительная информация */}
        <div className="w-full border-t border-gray-200 pt-6 text-center dark:border-gray-700">
          <p className="text-xs text-gray-500 dark:text-gray-500">
            Это референсная реализация для разработки
          </p>
          <p className="mt-1 text-xs text-gray-500 dark:text-gray-500">
            Backend: FastAPI (Python) • Frontend: Next.js
          </p>
        </div>
      </main>
    </div>
  );
}
