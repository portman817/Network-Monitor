export async function requestDevices(options = {}) {
  let response;
  try {
    response = await fetch('/api/devices', options);
  } catch (error) {
    if (error.name === 'AbortError') throw error;
    throw new Error('Нет соединения с backend. Проверьте подключение и повторите попытку.');
  }
  if (!response.ok) {
    if (response.status === 409) throw new Error('Устройство с таким адресом уже существует.');
    if (response.status === 422) {
      throw new Error('Проверьте название и адрес: укажите IP-адрес или доменное имя без протокола, порта и пути.');
    }
    throw new Error(`Не удалось выполнить запрос (HTTP ${response.status}). Повторите попытку.`);
  }
  try {
    return await response.json();
  } catch {
    throw new Error('Backend вернул некорректный ответ. Повторите попытку.');
  }
}

export async function getDevices(signal) {
  const devices = await requestDevices({ signal });
  if (!Array.isArray(devices)) throw new Error('Backend вернул некорректный список устройств.');
  return devices;
}

export function addDevice(device) {
  return requestDevices({
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(device),
  });
}
