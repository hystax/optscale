import messagesEnUS from "./en-US/index";

export default (() => {
  const DEFAULT_LOCALE = "en-US";

  const getCurrencyConfiguration = (currency, rest = {}) => ({
    style: "currency",
    currency,
    minimumFractionDigits: 0,
    ...rest
  });

  const getCompactCurrencyConfiguration = (currency, rest = {}) => ({
    style: "currency",
    currency,
    maximumFractionDigits: 1,
    minimumFractionDigits: 0,
    ...rest
  });

  const localeConfigMap = {
    [DEFAULT_LOCALE]: {
      formats: {
        number: {
          USD: getCurrencyConfiguration("USD"),
          USDCompact: getCompactCurrencyConfiguration("USD"),
          EUR: getCurrencyConfiguration("EUR"),
          EURCompact: getCompactCurrencyConfiguration("EUR"),
          CAD: getCurrencyConfiguration("CAD"),
          CADCompact: getCompactCurrencyConfiguration("CAD"),
          BRL: getCurrencyConfiguration("BRL"),
          BRLCompact: getCompactCurrencyConfiguration("BRL"),
          RUB: getCurrencyConfiguration("RUB", { currencyDisplay: "narrowSymbol" }),
          RUBCompact: getCompactCurrencyConfiguration("RUB", { currencyDisplay: "narrowSymbol" }),
          percentage: {
            style: "percent"
          },
          percentage2: {
            style: "percent",
            maximumFractionDigits: 2,
            minimumFractionDigits: 0
          }
        }
      }
    }
  };

  const messagesMap = {
    [DEFAULT_LOCALE]: messagesEnUS
  };

  const locale = messagesMap[navigator.language] ? navigator.language : DEFAULT_LOCALE;

  const getConfig = () => ({ ...localeConfigMap[locale], locale, messages: messagesMap[locale] });

  return {
    getConfig
  };
})();
