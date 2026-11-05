import { useEffect, useState } from 'react';

export default function App() {
  const [message, setMessage] = useState('Проверяем соединение с backend…');

  useEffect(() => {
    const controller = new AbortController();

    async function checkHealth() {
      try {
        const response = await fetch('/api/health', {
          signal: controller.signal,
        });
        if (!response.ok) throw new Error('Ошибка HTTP');
        const data = await response.json();
        if (data.status !== 'ok') throw new Error('Неожиданный ответ');
        setMessage('Backend доступен: ok');
      } catch {
        if (!controller.signal.aborted) {
          setMessage('Нет соединения с backend. Запустите сервер и обновите страницу.');
        }
      }
    }

    checkHealth();
    return () => controller.abort();
  }, []);

  return (
    <main>
      <h1>Network Monitor</h1>
      <p>Учебный проект мониторинга доступности сетевых устройств.</p>
      <p role="status">{message}</p>
    </main>
  );
}
