import { useEffect, useRef, useState } from 'react';
import { addDevice, discoverBatch, getDiscoverySubnets } from '../api/devices';
import { errorMessage, formatLatency, t } from '../i18n';

export default function DeviceDiscovery({ devices, onCreated }) {
  const [subnets, setSubnets] = useState(null);
  const [subnet, setSubnet] = useState('');
  const [found, setFound] = useState([]);
  const [progress, setProgress] = useState(null);
  const [running, setRunning] = useState(false);
  const [stopping, setStopping] = useState(false);
  const [skipped, setSkipped] = useState(0);
  const [adding, setAdding] = useState(null);
  const [error, setError] = useState(null);
  const scan = useRef(null);

  useEffect(() => {
    const controller = new AbortController();
    getDiscoverySubnets(controller.signal).then((values) => {
      setSubnets(values);
      setSubnet(values[0] ?? '');
    }).catch((failure) => {
      if (!controller.signal.aborted) setError(failure);
    });
    return () => {
      controller.abort();
      scan.current?.controller.abort();
    };
  }, []);

  async function discover() {
    if (!subnet || scan.current) return;
    const controller = new AbortController();
    const currentScan = { controller, stopRequested: false };
    scan.current = currentScan;
    setRunning(true);
    setError(null);
    setFound([]);
    setProgress(null);
    setSkipped(0);
    try {
      let offset = 0;
      while (offset !== null && !currentScan.stopRequested && !controller.signal.aborted) {
        const batch = await discoverBatch(subnet, offset, controller.signal);
        setFound((current) => [...current, ...batch.found]);
        setProgress({ checked: batch.checked, total: batch.total });
        setSkipped((current) => current + batch.skipped);
        offset = batch.next_offset;
      }
    } catch (failure) {
      if (!controller.signal.aborted) setError(failure);
    } finally {
      scan.current = null;
      setRunning(false);
      setStopping(false);
    }
  }

  async function add(address) {
    setAdding(address);
    setError(null);
    try {
      onCreated(await addDevice({ name: address, address }));
    } catch (failure) {
      setError(failure);
    } finally {
      setAdding(null);
    }
  }

  return (
    <section className="panel" aria-labelledby="discovery-heading">
      <h2 id="discovery-heading">{t('discoveryHeading')}</h2>
      {subnets?.length === 0 && <p>{t('discoveryNoSubnet')}</p>}
      {subnets?.length > 0 && (
        <>
          <label htmlFor="discovery-subnet">{t('discoverySubnet')}
            <select id="discovery-subnet" value={subnet} disabled={running}
              onChange={(event) => {
                setSubnet(event.target.value);
                setFound([]);
                setProgress(null);
                setSkipped(0);
                setError(null);
              }}>
              {subnets.map((value) => <option key={value}>{value}</option>)}
            </select>
          </label>
          <p>{t('discoveryHint')}</p>
          <div className="device-actions">
            <button onClick={discover} disabled={running}>{t('discoveryStart')}</button>
            {running && <button className="secondary" disabled={stopping} onClick={() => {
              scan.current.stopRequested = true;
              setStopping(true);
            }}>
              {t(stopping ? 'discoveryStopping' : 'discoveryStop')}
            </button>}
          </div>
        </>
      )}
      {error && <p className="error" role="alert">{errorMessage(error)}</p>}
      {progress && <p role="status">{t('discoveryProgress', progress)}</p>}
      {skipped > 0 && <p>{t('discoverySkipped', { count: skipped })}</p>}
      {found.length > 0 && <ul>{found.map(({ address, latency_ms: latency }) => {
        const saved = devices.some((device) => device.address === address);
        return <li key={address} className="device-actions">
          <span>{address} · {formatLatency(latency)}</span>
          <button className="secondary" disabled={saved || adding !== null} onClick={() => add(address)}>
            {t(saved ? 'discoverySaved' : 'addHeading')}
          </button>
        </li>;
      })}</ul>}
    </section>
  );
}
