import { afterEach, test } from 'node:test';
import assert from 'node:assert/strict';
import { addDevice, checkDevice, getDevices, getHealth, requestDevices, retryAfterSeconds, updateDevice } from './devices.js';

const originalFetch = globalThis.fetch;
afterEach(() => { globalThis.fetch = originalFetch; });
const device = { id: 1, name: 'Router', address: '127.0.0.1', status: 'unknown', latency_ms: null, last_checked_at: null };

test('GET returns full devices and forwards abort', async () => {
  const controller = new AbortController();
  globalThis.fetch = async (url, options) => {
    assert.equal(url, '/api/devices');
    assert.equal(options.signal.aborted, false);
    controller.abort();
    assert.equal(options.signal.aborted, true);
    throw new DOMException('Aborted', 'AbortError');
  };
  await assert.rejects(getDevices(controller.signal), { name: 'AbortError' });
});

test('GET validates and returns devices', async () => {
  globalThis.fetch = async () => Response.json([device]);
  assert.deepEqual(await getDevices(), [device]);
});

test('POST encodes name and address', async () => {
  globalThis.fetch = async (url, options) => {
    assert.equal(url, '/api/devices'); assert.equal(options.method, 'POST');
    assert.equal(options.headers['Content-Type'], 'application/json');
    assert.deepEqual(JSON.parse(options.body), { name: 'Router', address: '127.0.0.1' });
    return Response.json(device, { status: 201 });
  };
  assert.deepEqual(await addDevice({ name: 'Router', address: '127.0.0.1' }), device);
});

test('PUT sends edited fields and reports duplicate addresses', async () => {
  const edited = { name: 'New name', address: 'router.local' };
  globalThis.fetch = async (url, options) => {
    assert.equal(url, '/api/devices/1');
    assert.equal(options.method, 'PUT');
    assert.deepEqual(JSON.parse(options.body), edited);
    return Response.json({ detail: { code: 'duplicate_address' } }, { status: 409 });
  };
  await assert.rejects(updateDevice(1, edited), { code: 'duplicate_address' });
});

test('check returns zero RTT and UTC', async () => {
  globalThis.fetch = async (url, options) => {
    assert.equal(url, '/api/devices/1/check'); assert.equal(options.method, 'POST');
    return Response.json({ ...device, status: 'online', latency_ms: 0, last_checked_at: '2026-11-06T12:00:00Z' });
  };
  assert.equal((await checkDevice(1)).latency_ms, 0);
});

for (const [code, status] of [['target_forbidden',403], ['device_not_found',404], ['check_in_progress',409],
  ['check_rate_limited',429], ['ping_process_timeout',504], ['storage_unavailable',503],
  ['platform_unsupported',503], ['duplicate_address',409]]) {
  test(`reports structured ${code}`, async () => {
    globalThis.fetch = async () => Response.json({ detail: { code } }, { status, headers: {'Retry-After':'7'} });
    await assert.rejects(checkDevice(1), (error) => error.code === code && !!error.message
      && (status !== 429 || error.retryAfter === 7));
  });
}

test('validation errors are associated with fields', async () => {
  globalThis.fetch = async () => Response.json({ detail: [{loc:['body','name']}, {loc:['body','address']}] }, {status:422});
  await assert.rejects(addDevice({}), (error) => !!error.fields.name && !!error.fields.address);
});

test('non-JSON proxy error stays an HTTP error', async () => {
  globalThis.fetch = async () => new Response('Bad Gateway', {status:502});
  await assert.rejects(getDevices(), /HTTP 502/);
});

test('network error is understandable', async () => {
  globalThis.fetch = async () => { throw new TypeError('Failed'); };
  await assert.rejects(getDevices(), (error) => error.code === 'network_error');
});

for (const payload of [{}, [null], [{...device,status:'up'}], [{...device,latency_ms:-1}]]) {
  test(`invalid list ${JSON.stringify(payload)} is rejected`, async () => {
    globalThis.fetch = async () => Response.json(payload);
    await assert.rejects(getDevices(), (error) => error.code === 'invalid_response');
  });
}

test('malformed JSON is rejected', async () => {
  globalThis.fetch = async () => new Response('broken');
  await assert.rejects(getDevices(), (error) => error.code === 'invalid_response');
});

test('health uses existing endpoint', async () => {
  globalThis.fetch = async (url) => { assert.equal(url, '/api/health'); return Response.json({status:'ok'}); };
  await getHealth();
});

test('Retry-After parses seconds and HTTP date', () => {
  const now = Date.parse('2026-11-06T12:00:00Z');
  assert.equal(retryAfterSeconds('9', now), 9);
  assert.equal(retryAfterSeconds('Fri, 06 Nov 2026 12:00:12 GMT', now), 12);
  assert.equal(retryAfterSeconds('broken', now), 5);
  assert.equal(retryAfterSeconds(null, now), 5);
});

test('timeout bounds fetch wait and warns about uncertain writes', async () => {
  const keepAlive = setTimeout(() => {}, 1000);
  globalThis.fetch = async (url, {signal}) => new Promise((resolve, reject) => {
    signal.addEventListener('abort', () => reject(signal.reason), {once:true});
  });
  try { await assert.rejects(requestDevices({}, '/api/devices', 10), (error) => error.code === 'request_timeout'); }
  finally { clearTimeout(keepAlive); }
});

test('timeout also bounds response-body reading', async () => {
  const keepAlive = setTimeout(() => {}, 1000);
  globalThis.fetch = async (url, {signal}) => ({ok:true, json: () => new Promise((resolve,reject) => {
    signal.addEventListener('abort', () => reject(signal.reason), {once:true});
  })});
  try { await assert.rejects(requestDevices({}, '/api/devices', 10), (error) => error.code === 'request_timeout'); }
  finally { clearTimeout(keepAlive); }
});
