import { errorMessage } from '../i18n/index.js';

export const REQUEST_TIMEOUT_MS = 10000;
export class ApiError extends Error {
  constructor(code, { status = 0, fields = {}, retryAfter = 0 } = {}) {
    super();
    this.code = code;
    this.status = status;
    this.fields = fields;
    this.retryAfter = retryAfter;
  }
  get message() { return errorMessage(this); }
}

export function retryAfterSeconds(value, now = Date.now()) {
  if (!value) return 5;
  const seconds = /^\d+$/.test(value) ? Number(value) : (Date.parse(value) - now) / 1000;
  return Number.isFinite(seconds) ? Math.min(3600, Math.max(1, Math.ceil(seconds))) : 5;
}

export async function requestDevices(options = {}, url = '/api/devices', timeoutMs = REQUEST_TIMEOUT_MS) {
  const timeout = AbortSignal.timeout(timeoutMs);
  const signal = options.signal ? AbortSignal.any([options.signal, timeout]) : timeout;
  try {
    const response = await fetch(url, { ...options, signal });
    if (response.status === 204) return;
    let data;
    try { data = await response.json(); } catch (error) {
      if (signal.aborted) throw error;
      if (response.ok) throw new ApiError('invalid_response');
    }
    if (!response.ok) {
      const detail = data?.detail;
      const fields = {};
      if (Array.isArray(detail)) {
        for (const item of detail) {
          const field = item.loc?.[0] === 'body' ? item.loc[1] : null;
          if (field === 'name' || field === 'address') fields[field] = `invalid_${field}`;
        }
      }
      let code = detail?.code;
      if (!code) code = response.status === 409 && url === '/api/devices' ? 'duplicate_address'
        : response.status === 422 ? 'validation_error' : 'request_failed';
      throw new ApiError(code, { status: response.status, fields,
        retryAfter: response.status === 429 ? retryAfterSeconds(response.headers.get('Retry-After')) : 0 });
    }
    return data;
  } catch (error) {
    if (options.signal?.aborted) throw new DOMException('Aborted', 'AbortError');
    if (timeout.aborted) throw new ApiError('request_timeout');
    if (error instanceof ApiError) throw error;
    throw new ApiError('network_error');
  }
}

function validateDevice(device) {
  if (!device || !Number.isSafeInteger(device.id) || typeof device.name !== 'string'
    || typeof device.address !== 'string' || !['unknown', 'online', 'offline'].includes(device.status)
    || !(device.latency_ms === null || (Number.isFinite(device.latency_ms) && device.latency_ms >= 0))
    || !(device.last_checked_at === null || (typeof device.last_checked_at === 'string'
      && !Number.isNaN(Date.parse(device.last_checked_at))))) throw new ApiError('invalid_response');
  return device;
}

export async function getDevices(signal) {
  const devices = await requestDevices({ signal });
  if (!Array.isArray(devices)) throw new ApiError('invalid_response');
  return devices.map(validateDevice);
}

export async function addDevice(device) {
  return validateDevice(await requestDevices({ method: 'POST',
    headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(device) }));
}

export async function updateDevice(id, device) {
  return validateDevice(await requestDevices({ method: 'PUT',
    headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(device) }, `/api/devices/${id}`));
}

export async function checkDevice(id) {
  return validateDevice(await requestDevices({ method: 'POST' }, `/api/devices/${id}/check`));
}

export function deleteDevice(id) {
  return requestDevices({ method: 'DELETE' }, `/api/devices/${id}`);
}

export async function getHealth(signal) {
  const data = await requestDevices({ signal }, '/api/health');
  if (data?.status !== 'ok') throw new ApiError('invalid_response');
}

export async function getDiscoverySubnets(signal) {
  const subnets = await requestDevices({ signal }, '/api/devices/discovery');
  if (!Array.isArray(subnets) || subnets.some((subnet) => typeof subnet !== 'string')) {
    throw new ApiError('invalid_response');
  }
  return subnets;
}

export async function discoverBatch(subnet, offset, signal) {
  const batch = await requestDevices({
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ subnet, offset }),
    signal,
  }, '/api/devices/discovery', 25000);
  if (!Array.isArray(batch?.found) || !Number.isInteger(batch.skipped) || batch.skipped < 0
    || (batch.next_offset !== null
    && (!Number.isInteger(batch.next_offset) || batch.next_offset <= offset || batch.next_offset > 254))) {
    throw new ApiError('invalid_response');
  }
  return batch;
}
