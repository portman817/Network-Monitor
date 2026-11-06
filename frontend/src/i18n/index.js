import en from './en.js';

// Add separate de.js and ru.js dictionaries here when translations are approved.
const dictionaries = { en };
export const locale = 'en';

export function translate(key, values = {}, language = locale) {
  const template = dictionaries[language]?.[key] ?? en[key] ?? key;
  return template.replace(/\{(\w+)\}/g, (match, name) => String(values[name] ?? match));
}
export const t = translate;

export function formatCheckedAt(value) {
  if (!value) return t('noData');
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? t('noData') : date.toLocaleString(locale);
}

export function formatLatency(value) {
  return value == null ? t('noData') : t('latencyValue', { value: new Intl.NumberFormat(locale).format(value) });
}
