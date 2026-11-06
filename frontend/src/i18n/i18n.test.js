import { afterEach, test } from 'node:test';
import assert from 'node:assert/strict';
import {locale, translate, formatCheckedAt, formatLatency, setLocale, resolveLanguage, initialLanguage, dictionaries, languageKey, errorMessage} from './index.js';
import {ApiError} from '../api/devices.js';

afterEach(() => setLocale('en', {}));
test('all dictionaries have matching keys and placeholders', () => {
  for (const language of ['de','ru']) {
    assert.deepEqual(Object.keys(dictionaries[language]).sort(), Object.keys(dictionaries.en).sort());
    for (const key of Object.keys(dictionaries.en)) {
      assert.deepEqual(dictionaries[language][key].match(/\{\w+\}/g), dictionaries.en[key].match(/\{\w+\}/g));
    }
  }
});
test('saved choice precedes regional browser languages and English fallback', () => {
  assert.equal(resolveLanguage('ru', ['de-DE']), 'ru');
  assert.equal(resolveLanguage('bad', ['fr-FR','de-AT']), 'de');
  assert.equal(resolveLanguage(null, ['ru-RU']), 'ru');
  assert.equal(resolveLanguage(null, ['EN-gb']), 'en');
  assert.equal(resolveLanguage(null, ['fr-FR']), 'en');
  assert.equal(resolveLanguage(null, []), 'en');
});
test('storage access failures do not break initialization or switching', () => {
  const environment = {navigator:{languages:['de-DE']}, get localStorage() {throw new Error('blocked');}};
  assert.equal(initialLanguage(environment), 'de');
  setLocale('ru', environment);
  assert.equal(locale, 'ru');
});
test('manual choice persists and updates HTML language', () => {
  let saved;
  const environment = {localStorage:{setItem:(key,value)=>{assert.equal(key,languageKey);saved=value;}},document:{documentElement:{lang:'en'}}};
  setLocale('de', environment);
  assert.equal(saved,'de'); assert.equal(environment.document.documentElement.lang,'de');
  assert.equal(initialLanguage({localStorage:{getItem:()=>saved},navigator:{languages:['ru']}}),'de');
  setLocale('invalid',environment); assert.equal(locale,'de');
});
test('English fallback and interpolation treat inserted text as data', () => {
  assert.equal(translate('add', {}, 'xx'), 'Add device');
  assert.equal(translate('created', {name:'{value}<script>'},'en'), 'Device “{value}<script>” added.');
  assert.equal(translate('constructor'), 'constructor');
});
test('existing errors and field keys translate after a language change', () => {
  const error = new ApiError('duplicate_address');
  assert.match(error.message,/already exists/);
  setLocale('de',{}); assert.match(errorMessage(error),/bereits vorhanden/);
  setLocale('ru',{}); assert.equal(errorMessage(error), dictionaries.ru.duplicate_address);
  assert.equal(translate('invalid_name'),dictionaries.ru.invalid_name);
});
test('dates and numbers follow the current language without changing values', () => {
  const value = '2026-11-06T12:00:00Z';
  for (const language of ['en','de','ru']) {
    setLocale(language,{});
    assert.equal(formatCheckedAt(value),new Date(value).toLocaleString(language));
    assert.equal(formatLatency(1.5),translate('latencyValue',{value:new Intl.NumberFormat(language).format(1.5)}));
    assert.equal(formatCheckedAt('bad'),translate('noData'));
    assert.equal(formatLatency(null),translate('noData'));
  }
});
