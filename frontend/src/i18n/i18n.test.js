import {test} from 'node:test';
import assert from 'node:assert/strict';
import {locale, translate, formatCheckedAt, formatLatency} from './index.js';

test('English is default with fallback for future languages', () => {
  assert.equal(locale, 'en');
  for (const language of ['en','de','ru','xx']) assert.equal(translate('add', {}, language), 'Add device');
});
test('interpolates user text as data without recursive replacement', () => {
  assert.equal(translate('created', {name:'{value}<script>'}), 'Device “{value}<script>” added.');
});
test('formats missing values and zero RTT', () => {
  assert.equal(formatCheckedAt(null), 'No data');
  assert.equal(formatCheckedAt('bad'), 'No data');
  assert.equal(formatLatency(null), 'No data');
  assert.equal(formatLatency(0), '0 ms');
});
