import { useRef, useState } from 'react';
import { addDevice } from '../api/devices';

export default function DeviceForm({ onCreated }) {
  const [name, setName] = useState('');
  const [address, setAddress] = useState('');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const pending = useRef(false);

  async function handleSubmit(event) {
    event.preventDefault();
    if (pending.current) return;
    setError('');
    setSuccess('');
    if (!name.trim() || !address.trim()) {
      setError('Заполните название и адрес устройства.');
      return;
    }
    pending.current = true;
    setSaving(true);
    try {
      const device = await addDevice({ name: name.trim(), address: address.trim() });
      setName('');
      setAddress('');
      setSuccess(`Устройство «${device.name}» добавлено.`);
      onCreated(device);
    } catch (error) {
      setError(error.message);
    } finally {
      pending.current = false;
      setSaving(false);
    }
  }

  return (
    <section className="panel" aria-labelledby="add-device-heading">
      <h2 id="add-device-heading">Добавить устройство</h2>
      <form onSubmit={handleSubmit} aria-busy={saving}>
        <fieldset disabled={saving}>
          <div className="form-fields">
            <label htmlFor="device-name">Название
              <input id="device-name" name="name" value={name} onChange={(e) => setName(e.target.value)}
                required maxLength={100} placeholder="Например, домашний роутер" />
            </label>
            <label htmlFor="device-address">IP-адрес или доменное имя
              <input id="device-address" name="address" value={address} onChange={(e) => setAddress(e.target.value)}
                required maxLength={1024} spellCheck={false} autoCapitalize="none" autoCorrect="off"
                aria-describedby="address-help" placeholder="192.168.1.1 или router.local" />
            </label>
          </div>
          <p id="address-help" className="muted">Укажите адрес без протокола, порта и пути.</p>
          <button type="submit">{saving ? 'Сохраняем…' : 'Добавить устройство'}</button>
        </fieldset>
        {error && <p className="error" role="alert">{error}</p>}
        <p className="success" role="status">{success}</p>
      </form>
    </section>
  );
}
