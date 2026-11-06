const statusLabels = { unknown: 'Неизвестен', online: 'Доступно', offline: 'Нет ICMP-ответа' };

function checkedAt(value) {
  if (!value) return 'Нет данных';
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? 'Нет данных' : date.toLocaleString('ru-RU');
}

export default function DeviceList({ devices, loading, error, onRefresh, onCheck, checking, checkErrors }) {
  return (
    <section className="panel" aria-labelledby="devices-heading" aria-busy={loading}>
      <div className="section-heading">
        <h2 id="devices-heading">Устройства <span className="count">{devices.length}</span></h2>
        <button className="secondary" onClick={onRefresh} disabled={loading}>
          {loading ? 'Загружаем…' : 'Обновить список'}
        </button>
      </div>
      {error && <p className="error" role="alert">{error} Нажмите «Обновить список», чтобы повторить запрос.</p>}
      {loading && <p role="status">Загружаем устройства…</p>}
      {!loading && !error && devices.length === 0 && (
        <p className="muted">Устройств пока нет. Добавьте первое устройство с помощью формы выше.</p>
      )}
      {devices.length > 0 && (
        <div className="table-scroll">
          <table>
            <caption className="sr-only">Сохранённые сетевые устройства</caption>
            <thead><tr><th scope="col">Название</th><th scope="col">Адрес</th><th scope="col">Статус</th>
              <th scope="col">Задержка</th><th scope="col">Последняя проверка</th><th scope="col">Проверка</th></tr></thead>
            <tbody>{devices.map((device) => (
              <tr key={device.id}>
                <td>{device.name}</td><td className="address">{device.address}</td>
                <td><span className="badge">{statusLabels[device.status] ?? device.status}</span></td>
                <td>{device.latency_ms == null ? 'Нет данных' : `${device.latency_ms} мс`}</td>
                <td>{checkedAt(device.last_checked_at)}</td>
                <td>
                  <button className="secondary" onClick={() => onCheck(device.id)} disabled={checking.has(device.id)}
                    aria-label={`Проверить ${device.name}`}>
                    {checking.has(device.id) ? 'Проверяем…' : 'Проверить'}
                  </button>
                  {checkErrors[device.id] && <p className="error" role="alert">{checkErrors[device.id]}</p>}
                </td>
              </tr>
            ))}</tbody>
          </table>
        </div>
      )}
    </section>
  );
}
