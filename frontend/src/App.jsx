import { useEffect, useRef, useState } from 'react';
import { getDevices } from './api/devices';
import DeviceForm from './components/DeviceForm';
import DeviceList from './components/DeviceList';

export default function App() {
  const [message, setMessage] = useState('Проверяем соединение с backend…');
  const [devices, setDevices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const listRequest = useRef(null);

  async function loadDevices() {
    listRequest.current?.abort();
    const controller = new AbortController();
    listRequest.current = controller;
    setLoading(true);
    setError('');
    try {
      const data = await getDevices(controller.signal);
      if (!controller.signal.aborted) setDevices(data);
    } catch (error) {
      if (!controller.signal.aborted) setError(error.message);
    } finally {
      if (!controller.signal.aborted) setLoading(false);
    }
  }

  useEffect(() => {
    loadDevices();
    return () => listRequest.current?.abort();
  }, []);

  function handleCreated(device) {
    listRequest.current?.abort();
    setDevices((current) => [...current.filter((item) => item.id !== device.id), device]
      .sort((a, b) => a.id - b.id));
    loadDevices();
  }

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
      <header>
        <p className="eyebrow">Управление сетевыми устройствами</p>
        <h1>Network Monitor</h1>
        <p>Добавляйте устройства и просматривайте сохранённые данные.</p>
        <p className="muted" role="status">{message}</p>
      </header>
      <DeviceForm onCreated={handleCreated} />
      <DeviceList devices={devices} loading={loading} error={error} onRefresh={loadDevices} />
      <p className="muted">Проверки доступности пока не выполняются. Новые устройства имеют статус «Неизвестен».</p>
    </main>
  );
}
