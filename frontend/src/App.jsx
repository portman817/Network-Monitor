import { useEffect, useRef, useState } from 'react';
import { checkDevice, getDevices, getHealth } from './api/devices';
import { locale, t, useLocale, setLocale, languages } from './i18n';
import DeviceForm from './components/DeviceForm';
import DeviceList from './components/DeviceList';

export default function App() {
  const language = useLocale();
  const [health, setHealth] = useState('healthLoading');
  const [devices, setDevices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const listRequest = useRef(null);
  const checkingRef = useRef(new Set());
  const [checking, setChecking] = useState(new Set());
  const [checkErrors, setCheckErrors] = useState({});
  const [cooldowns, setCooldowns] = useState({});

  async function loadDevices() {
    listRequest.current?.abort();
    const controller = new AbortController();
    listRequest.current = controller;
    setLoading(true);
    setHealth('healthLoading');
    setError('');
    getHealth(controller.signal).then(() => {
      if (!controller.signal.aborted) setHealth('healthOk');
    }).catch(() => {
      if (!controller.signal.aborted) setHealth('healthError');
    });
    try {
      const data = await getDevices(controller.signal);
      if (!controller.signal.aborted) setDevices(data);
    } catch (error) {
      if (!controller.signal.aborted) setError(error);
    } finally {
      if (!controller.signal.aborted) setLoading(false);
    }
  }

  async function handleCheck(id) {
    if (checkingRef.current.has(id) || (cooldowns[id] ?? 0) > Date.now()) return;
    checkingRef.current.add(id);
    setChecking(new Set(checkingRef.current));
    setCheckErrors((current) => ({ ...current, [id]: '' }));
    try {
      const updated = await checkDevice(id);
      listRequest.current?.abort();
      setDevices((current) => current.map((device) => device.id === id ? updated : device));
      setCooldowns((current) => ({ ...current, [id]: Date.now() + 5000 }));
      loadDevices();
    } catch (error) {
      setCheckErrors((current) => ({ ...current, [id]: error }));
      if (error.retryAfter) setCooldowns((current) => ({ ...current, [id]: Date.now() + error.retryAfter * 1000 }));
      if (['network_error', 'request_timeout'].includes(error.code)) setHealth('healthError');
    } finally {
      checkingRef.current.delete(id);
      setChecking(new Set(checkingRef.current));
    }
  }

  useEffect(() => {
    document.documentElement.lang = locale;
    loadDevices();
    return () => listRequest.current?.abort();
  }, []);

  function handleCreated(device) {
    listRequest.current?.abort();
    setDevices((current) => [...current.filter((item) => item.id !== device.id), device].sort((a, b) => a.id - b.id));
    loadDevices();
  }

  return (
    <main>
      <header><label className="language-picker" htmlFor="language">{t('language')}
        <select id="language" value={language} onChange={(event) => setLocale(event.target.value)}>
          {languages.map((code) => <option key={code} value={code}>{t(`language_${code}`)}</option>)}
        </select>
      </label><p className="eyebrow">{t('eyebrow')}</p><h1>{t('title')}</h1>
        <p>{t('intro')}</p><p className="muted" role="status">{t(health)}</p></header>
      <DeviceForm onCreated={handleCreated} />
      <DeviceList devices={devices} loading={loading} error={error} onRefresh={loadDevices}
        onCheck={handleCheck} checking={checking} checkErrors={checkErrors} cooldowns={cooldowns} />
      <p className="muted">{t('networkNotice')}</p>
    </main>
  );
}
