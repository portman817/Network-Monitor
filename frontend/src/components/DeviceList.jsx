import { useEffect, useState } from 'react';
import { formatCheckedAt, formatLatency, t, errorMessage } from '../i18n';

export default function DeviceList({ devices, loading, error, onRefresh, onDelete, onEdit, editingId,
  onCheck, checking, checkErrors, cooldowns }) {
  const [deleting, setDeleting] = useState(null);
  const [deleteError, setDeleteError] = useState(null);

  async function remove(device) {
    if (deleting !== null || !window.confirm(t('deleteConfirm', { name: device.name }))) return;
    setDeleteError(null);
    setDeleting(device.id);
    try {
      await onDelete(device.id);
    } catch (error) {
      setDeleteError(error);
    } finally {
      setDeleting(null);
    }
  }

  const [now, setNow] = useState(Date.now());
  useEffect(() => {
    if (!Object.values(cooldowns).some((deadline) => deadline > Date.now())) return;
    setNow(Date.now());
    const timer = setInterval(() => {
      const time = Date.now();
      setNow(time);
      if (Object.values(cooldowns).every((deadline) => deadline <= time)) clearInterval(timer);
    }, 500);
    return () => clearInterval(timer);
  }, [cooldowns]);
  return (
    <section className="panel" aria-labelledby="devices-heading" aria-busy={loading}>
      <div className="section-heading"><h2 id="devices-heading">{t('devices')} <span className="count">{devices.length}</span></h2>
        <button className="secondary" onClick={onRefresh} disabled={loading}>{t(loading ? 'loading' : 'refresh')}</button></div>
      {error && <p className="error" role="alert">{errorMessage(error)} {t('retry')}</p>}
      {deleteError && <p className="error" role="alert">{errorMessage(deleteError)}</p>}
      {loading && <p role="status">{t('loading')}</p>}
      {!loading && !error && devices.length === 0 && <p className="muted">{t('empty')}</p>}
      {devices.length > 0 && <div className="table-scroll" tabIndex={0} role="region" aria-label={t('caption')}>
        <table><caption className="sr-only">{t('caption')}</caption><thead><tr>
          {['name', 'address', 'status', 'latency', 'lastChecked', 'action'].map((key) => <th key={key} scope="col">{t(key)}</th>)}
        </tr></thead><tbody>{devices.map((device) => {
          const seconds = Math.max(0, Math.ceil(((cooldowns[device.id] ?? 0) - now) / 1000));
          const forbidden = device.check_allowed !== true;
          return <tr key={device.id}><td>{device.name}</td><td className="address">{device.address}</td>
            <td><span className={`badge status-${device.status}`}>{t(device.status)}</span></td>
            <td>{formatLatency(device.latency_ms)}</td><td>{formatCheckedAt(device.last_checked_at)}</td>
            <td>
              <div className="device-actions">
                <button className="secondary" onClick={() => onCheck(device.id)}
                  disabled={editingId === device.id || deleting === device.id || forbidden || checking.has(device.id) || seconds > 0}
                  aria-label={t('checkDevice', { name: device.name })}
                  aria-describedby={forbidden ? `check-help-${device.id}` : undefined}>
                  {checking.has(device.id) ? t('checking') : seconds > 0 ? t('cooldown', { seconds }) : t('action')}
                </button>
                <button className="secondary" onClick={() => onEdit(device)}
                  disabled={editingId != null || deleting === device.id || checking.has(device.id)}>
                  {t('editDevice')}
                </button>
                <button className="secondary danger" onClick={() => remove(device)}
                  disabled={editingId === device.id || deleting !== null || checking.has(device.id)}>
                  {t(deleting === device.id ? 'deleting' : 'deleteDevice')}
                </button>
              </div>
              {forbidden && <p id={`check-help-${device.id}`} className="muted">{t('forbiddenHint')}</p>}
              {checkErrors[device.id] && <p className="error" role="alert">{errorMessage(checkErrors[device.id])}</p>}
            </td></tr>;
        })}</tbody></table>
      </div>}
    </section>
  );
}
