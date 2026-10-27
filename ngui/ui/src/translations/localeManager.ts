import { currencyCodes } from "utils/currency";
import messagesEnUS from "./en-US/index";
import messagesEsES from "./es-ES/index";

const getCurrencySymbol = (currency, locale) =>
  new Intl.NumberFormat(locale, { style: "currency", currency, currencyDisplay: "narrowSymbol" })
    .formatToParts(1)
    .find((x) => x.type === "currency").value;

export const DEFAULT_LOCALE = "en-US";

export const SUPPORTED_LOCALES = {
  "en-US": "English",
  "es-ES": "Español",
} as const;

export type SupportedLocale = keyof typeof SUPPORTED_LOCALES;

const getCurrencyConfiguration = (currency, rest = {}) => ({
  style: "currency",
  currency,
  minimumFractionDigits: 0,
  ...rest,
});

const getCompactCurrencyConfiguration = (currency, rest = {}) => ({
  style: "currency",
  currency,
  maximumFractionDigits: 1,
  minimumFractionDigits: 0,
  ...rest,
});

const numberFormats = {
  ...Object.fromEntries(
    currencyCodes
      .map((code) => [
        [code, getCurrencyConfiguration(code, { currencyDisplay: "narrowSymbol" })],
        [`${code}Compact`, getCompactCurrencyConfiguration(code, { currencyDisplay: "narrowSymbol" })],
      ])
      .flat()
  ),
  percentage: {
    style: "percent",
  },
  percentage2: {
    style: "percent",
    maximumFractionDigits: 2,
    minimumFractionDigits: 0,
  },
};

const formats = { number: numberFormats };

const messagesMap: Record<SupportedLocale, Record<string, string>> = {
  "en-US": messagesEnUS,
  "es-ES": messagesEsES,
};

export const getMessagesForLocale = (locale: SupportedLocale): Record<string, string> => messagesMap[locale] ?? messagesEnUS;

export const getDefaultMessages = (): Record<string, string> => messagesEnUS;

export const getConfigForLocale = (locale: SupportedLocale) => ({
  locale,
  formats,
  messages: {
    ...messagesEnUS,
    ...getMessagesForLocale(locale),
  },
  defaultLocale: DEFAULT_LOCALE,
});

export default (() => {
  const locale = (messagesMap[navigator.language as SupportedLocale] ? navigator.language : DEFAULT_LOCALE) as SupportedLocale;

  const getConfig = () => getConfigForLocale(locale);

  return {
    getConfig,
    getCurrencySymbol: (currencyCode) => getCurrencySymbol(currencyCode, locale),
  };
})();
