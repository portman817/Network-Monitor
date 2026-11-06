import { afterEach, test } from 'node:test';
import assert from 'node:assert/strict';
import { addDevice, getDevices } from './devices.js';

const originalFetch = globalThis.fetch;
afterEach(() => { globalThis.fetch = originalFetch; });

test('GET passes cancellation signal and returns devices', async () => {
  const controller = new AbortController();
  globalThis.fetch = async (url, options) => {
    assert.equal(url, '/api/devices');
    assert.equal(options.signal, controller.signal);
    return Response.json([{ id: 1 }]);
  };
  assert.deepEqual(await getDevices(controller.signal), [{ id: 1 }]);
});

test('POST sends only supplied device fields as JSON', async () => {
  globalThis.fetch = async (url, options) => {
    assert.equal(url, '/api/devices');
    assert.equal(options.method, 'POST');
    assert.equal(options.headers['Content-Type'], 'application/json');
    assert.deepEqual(JSON.parse(options.body), { name: 'Router', address: 'router' });
    return Response.json({ id: 1, name: 'Router' }, { status: 201 });
  };
  assert.equal((await addDevice({ name: 'Router', address: 'router' })).id, 1);
});

for (const [status, message] of [[409, /уже существует/], [422, /Проверьте название/], [502, /HTTP 502/]]) {
  test(`HTTP ${status} becomes a useful error`, async () => {
    globalThis.fetch = async () => new Response('', { status });
    await assert.rejects(getDevices(), message);
  });
}

test('network failure becomes a connection error', async () => {
  globalThis.fetch = async () => { throw new TypeError('Failed to fetch'); };
  await assert.rejects(getDevices(), /Нет соединения/);
});

test('abort is preserved', async () => {
  const error = new DOMException('Aborted', 'AbortError');
  globalThis.fetch = async () => { throw error; };
  await assert.rejects(getDevices(), (caught) => caught === error);
});

test('invalid JSON is rejected', async () => {
  globalThis.fetch = async () => new Response('broken');
  await assert.rejects(getDevices(), /некорректный ответ/);
});

test('non-array list is rejected', async () => {
  globalThis.fetch = async () => Response.json({});
  await assert.rejects(getDevices(), /некорректный список/);
});
