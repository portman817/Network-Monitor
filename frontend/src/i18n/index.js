import { useSyncExternalStore } from 'react';
import en from './en.js';
import de from './de.js';
import ru from './ru.js';

export const dictionaries = { en, de, ru };
export const languageKey = 'network-monitor-language';
export const languages = Object.keys(dictionaries);

function normalizeLanguage(value) {
  if (typeof value !== 'string') return null;
  const language = value.toLowerCase().split('-')[0];
  return languages.includes(language) ? language : null;
}

export function resolveLanguage(saved, browserLanguages = []) {
  return normalizeLanguage(saved) ?? browserLanguages.map(normalizeLanguage).find(Boolean) ?? 'en';
}

export function initialLanguage(environment = globalThis) {
  let saved;
  try { saved = environment.localStorage?.getItem(languageKey); } catch { /* Storage may be blocked. */ }
  const browser = environment.navigator;
  return resolveLanguage(saved, browser?.languages?.length ? browser.languages : [browser?.language]);
}

export let locale = initialLanguage();
const listeners = new Set();
function subscribe(listener) { listeners.add(listener); return () => listeners.delete(listener); }
export function useLocale() { return useSyncExternalStore(subscribe, () => locale, () => 'en'); }

export function setLocale(language, environment = globalThis) {
  if (!languages.includes(language)) return;
  locale = language;
  try { environment.localStorage?.setItem(languageKey, locale); } catch { /* Keep in-memory choice. */ }
  if (environment.document) environment.document.documentElement.lang = locale;
  listeners.forEach((listener) => listener());
}

export function translate(key, values = {}, language = locale) {
  const dictionary = dictionaries[language];
  const template = (dictionary && Object.hasOwn(dictionary, key) ? dictionary[key] : undefined)
    ?? (Object.hasOwn(en, key) ? en[key] : key);
  return template.replace(/\{(\w+)\}/g, (match, name) => String(values[name] ?? match));
}
export const t = translate;

export function errorMessage(error) {
  if (!error) return '';
  if (error.code) {
    const text = t(error.code, { status: error.status ?? 0 });
    return text === error.code ? t('request_failed', {status: error.status ?? 0}) : text;
  }
  return error.message ?? t('request_failed', { status: 0 });
}

export function formatCheckedAt(value) {
  if (!value) return t('noData');
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? t('noData') : date.toLocaleString(locale);
}

export function formatLatency(value) {
  return value == null ? t('noData') : t('latencyValue', { value: new Intl.NumberFormat(locale).format(value) });
}
