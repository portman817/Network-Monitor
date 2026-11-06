import { useRef, useState } from 'react';
import { addDevice } from '../api/devices';
import { t, errorMessage } from '../i18n';

export default function DeviceForm({ onCreated }) {
  const [name, setName] = useState('');
  const [address, setAddress] = useState('');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [fields, setFields] = useState({});
  const [success, setSuccess] = useState('');
  const pending = useRef(false);

  async function handleSubmit(event) {
    event.preventDefault();
    if (pending.current) return;
    setError(''); setSuccess(''); setFields({});
    const invalid = {};
    if (!name.trim()) invalid.name = 'required';
    if (!address.trim()) invalid.address = 'required';
    if (Object.keys(invalid).length) { setFields(invalid); return; }
    pending.current = true;
    setSaving(true);
    try {
      const device = await addDevice({ name: name.trim(), address: address.trim() });
      setName(''); setAddress('');
      setSuccess(device.name);
      onCreated(device);
    } catch (error) {
      setError(error);
      setFields(error.fields ?? {});
    } finally {
      pending.current = false;
      setSaving(false);
    }
  }

  return (
    <section className="panel" aria-labelledby="add-device-heading">
      <h2 id="add-device-heading">{t('addHeading')}</h2>
      <form onSubmit={handleSubmit} aria-busy={saving}>
        <fieldset disabled={saving}><div className="form-fields">
          <div><label htmlFor="device-name">{t('name')}
            <input id="device-name" name="name" value={name} onChange={(e) => setName(e.target.value)}
              required maxLength={100} placeholder={t('namePlaceholder')} aria-invalid={!!fields.name}
              aria-describedby={fields.name ? 'name-error' : undefined} />
          </label>
            {fields.name && <span id="name-error" className="field-error" role="alert">{t(fields.name)}</span>}
          </div>
          <div><label htmlFor="device-address">{t('address')}
            <input id="device-address" name="address" value={address} onChange={(e) => setAddress(e.target.value)}
              required maxLength={1024} spellCheck={false} autoCapitalize="none" autoCorrect="off"
              aria-invalid={!!fields.address} aria-describedby={`address-help${fields.address ? ' address-error' : ''}`}
              placeholder={t('addressPlaceholder')} />
          </label>
            {fields.address && <span id="address-error" className="field-error" role="alert">{t(fields.address)}</span>}
          </div>
        </div><p id="address-help" className="muted">{t('addressHelp')}</p>
          <button type="submit">{t(saving ? 'saving' : 'add')}</button>
        </fieldset>
        {error && <p className="error" role="alert">{errorMessage(error)}</p>}
        <p className="success" role="status">{success ? t('created', { name: success }) : ''}</p>
      </form>
    </section>
  );
}
