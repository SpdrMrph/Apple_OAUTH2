'use client';

import { useEffect, useState } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';

const BACKEND_URL = 'http://localhost:8000';

interface UserData {
  user_id: string;
  email: string;
  email_verified: boolean;
  is_private_email: boolean;
}

export default function CallbackPage() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [userData, setUserData] = useState<UserData | null>(null);
  const [sessionId, setSessionId] = useState('');

  useEffect(() => {
    const handleCallback = async () => {
      // Проверяем параметры URL
      const errorParam = searchParams.get('error');
      const sessionIdParam = searchParams.get('session_id');

      if (errorParam) {
        setError(`Ошибка авторизации: ${errorParam}`);
        setLoading(false);
        return;
      }

      if (!sessionIdParam) {
        setError('Отсутствует session_id. Возможно произошла ошибка при авторизации.');
        setLoading(false);
        return;
      }

      setSessionId(sessionIdParam);

      try {
        // Получаем данные пользователя с backend
        const response = await fetch(
          `${BACKEND_URL}/auth/user?session_id=${sessionIdParam}`
        );

        if (!response.ok) {
          throw new Error('Не удалось получить данные пользователя');
        }

        const data = await response.json();
        setUserData(data);
        
        // Сохраняем session_id в localStorage для будущих запросов
        localStorage.setItem('apple_session_id', sessionIdParam);
        
      } catch (err) {
        console.error('Ошибка:', err);
        setError('Не удалось получить данные пользователя');
      } finally {
        setLoading(false);
      }
    };

    handleCallback();
  }, [searchParams]);

  const handleLogout = async () => {
    try {
      await fetch(`${BACKEND_URL}/auth/logout?session_id=${sessionId}`, {
        method: 'POST',
      });
      localStorage.removeItem('apple_session_id');
      router.push('/');
    } catch (err) {
      console.error('Ошибка при выходе:', err);
    }
  };

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-black">
        <div className="text-center">
          <div className="mb-4 inline-block h-12 w-12 animate-spin rounded-full border-4 border-gray-300 border-t-black dark:border-gray-700 dark:border-t-white"></div>
          <p className="text-gray-600 dark:text-gray-400">
            Загрузка данных пользователя...
          </p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-black">
        <div className="w-full max-w-md rounded-2xl bg-white p-12 shadow-2xl dark:bg-gray-800">
          <div className="mb-6 flex h-16 w-16 items-center justify-center rounded-full bg-red-100 dark:bg-red-900/20">
            <svg
              className="h-8 w-8 text-red-600 dark:text-red-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </div>
          <h1 className="mb-4 text-2xl font-bold text-gray-900 dark:text-white">
            Ошибка авторизации
          </h1>
          <p className="mb-6 text-gray-600 dark:text-gray-400">{error}</p>
          <button
            onClick={() => router.push('/')}
            className="w-full rounded-lg bg-black px-6 py-3 font-semibold text-white transition-colors hover:bg-gray-800 dark:bg-white dark:text-black dark:hover:bg-gray-200"
          >
            Вернуться на главную
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-black">
      <div className="w-full max-w-md rounded-2xl bg-white p-12 shadow-2xl dark:bg-gray-800">
        
        {/* Иконка успеха */}
        <div className="mb-6 flex h-16 w-16 items-center justify-center rounded-full bg-green-100 dark:bg-green-900/20">
          <svg
            className="h-8 w-8 text-green-600 dark:text-green-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M5 13l4 4L19 7"
            />
          </svg>
        </div>

        {/* Заголовок */}
        <h1 className="mb-2 text-3xl font-bold text-gray-900 dark:text-white">
          Успешная авторизация! ✅
        </h1>
        <p className="mb-8 text-sm text-gray-600 dark:text-gray-400">
          Вы успешно авторизовались через Apple ID
        </p>

        {/* Данные пользователя */}
        {userData && (
          <div className="mb-6 space-y-4 rounded-lg bg-gray-50 p-6 dark:bg-gray-900">
            <h2 className="mb-4 text-lg font-semibold text-gray-900 dark:text-white">
              Данные пользователя:
            </h2>
            
            <div>
              <p className="text-xs font-semibold uppercase text-gray-500 dark:text-gray-500">
                User ID
              </p>
              <p className="mt-1 break-all font-mono text-sm text-gray-900 dark:text-white">
                {userData.user_id}
              </p>
            </div>

            {userData.email && (
              <div>
                <p className="text-xs font-semibold uppercase text-gray-500 dark:text-gray-500">
                  Email
                </p>
                <p className="mt-1 font-mono text-sm text-gray-900 dark:text-white">
                  {userData.email}
                </p>
              </div>
            )}

            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-xs font-semibold uppercase text-gray-500 dark:text-gray-500">
                  Email Verified
                </p>
                <p className="mt-1 text-sm text-gray-900 dark:text-white">
                  {userData.email_verified ? '✅ Да' : '❌ Нет'}
                </p>
              </div>

              <div>
                <p className="text-xs font-semibold uppercase text-gray-500 dark:text-gray-500">
                  Private Email
                </p>
                <p className="mt-1 text-sm text-gray-900 dark:text-white">
                  {userData.is_private_email ? '🔒 Да' : '📧 Нет'}
                </p>
              </div>
            </div>

            <div className="rounded-md bg-blue-50 p-3 dark:bg-blue-900/20">
              <p className="text-xs text-blue-900 dark:text-blue-300">
                <strong>Session ID:</strong> <code className="text-xs">{sessionId.slice(0, 20)}...</code>
              </p>
              <p className="mt-1 text-xs text-blue-800 dark:text-blue-400">
                Сохранён в localStorage для будущих запросов
              </p>
            </div>
          </div>
        )}

        {/* Информация */}
        <div className="mb-6 rounded-lg bg-yellow-50 p-4 dark:bg-yellow-900/20">
          <p className="text-xs text-yellow-900 dark:text-yellow-300">
            <strong>💡 Примечание:</strong> Имя и фамилия пользователя передаются Apple 
            только при первой авторизации. При повторных входах они не будут доступны.
          </p>
        </div>

        {/* Кнопки */}
        <div className="flex gap-3">
          <button
            onClick={() => router.push('/')}
            className="flex-1 rounded-lg border border-gray-300 px-6 py-3 font-semibold text-gray-700 transition-colors hover:bg-gray-50 dark:border-gray-600 dark:text-gray-300 dark:hover:bg-gray-700"
          >
            На главную
          </button>
          <button
            onClick={handleLogout}
            className="flex-1 rounded-lg bg-black px-6 py-3 font-semibold text-white transition-colors hover:bg-gray-800 dark:bg-white dark:text-black dark:hover:bg-gray-200"
          >
            Выйти
          </button>
        </div>
      </div>
    </div>
  );
}


