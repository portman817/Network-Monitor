export async function requestDevices(options = {}, url = '/api/devices') {
  let response;
  try {
    response = await fetch(url, options);
  } catch (error) {
    if (error.name === 'AbortError') throw error;
    throw new Error('Нет соединения с backend. Проверьте подключение и повторите попытку.');
  }
  if (!response.ok) {
    if (url.endsWith('/check')) {
      const messages = {
        target_forbidden: 'Проверка разрешена только для 127.0.0.1. Другие адреса и домены запрещены.',
        device_not_found: 'Устройство не найдено. Обновите список.',
        check_in_progress: 'Проверка этого устройства уже выполняется.',
        check_rate_limited: 'Подождите 5 секунд и повторите проверку.',
        ping_process_timeout: 'Превышено время работы инструмента проверки. Предыдущие данные сохранены.',
        platform_unsupported: 'ICMP-проверки пока поддерживаются только в Windows.',
        storage_unavailable: 'Не удалось сохранить результат проверки.',
      };
      let code;
      try { code = (await response.json()).detail?.code; } catch { /* Non-JSON proxy response. */ }
      throw new Error(messages[code] ?? `Не удалось выполнить проверку (HTTP ${response.status}). Предыдущие данные сохранены.`);
    }
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

export function checkDevice(id) {
  return requestDevices({ method: 'POST' }, `/api/devices/${id}/check`);
}
