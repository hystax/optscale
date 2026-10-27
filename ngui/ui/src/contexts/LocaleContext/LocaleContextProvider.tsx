import { ReactNode, useCallback, useMemo, useState } from "react";
import { IntlProvider } from "react-intl";
import { DEFAULT_LOCALE, SupportedLocale, getConfigForLocale } from "translations/localeManager";
import LocaleContext from "./LocaleContext";

const LocaleContextProvider = ({ children }: { children: ReactNode }) => {
  const [locale, setLocaleState] = useState<SupportedLocale>(DEFAULT_LOCALE);

  const setLocale = useCallback((newLocale: SupportedLocale) => {
    setLocaleState(newLocale);
  }, []);

  const intlConfig = useMemo(() => getConfigForLocale(locale), [locale]);

  const contextValue = useMemo(() => ({ locale, setLocale }), [locale, setLocale]);

  return (
    <LocaleContext.Provider value={contextValue}>
      <IntlProvider
        locale={intlConfig.locale}
        messages={intlConfig.messages}
        formats={intlConfig.formats}
        defaultLocale={DEFAULT_LOCALE}
      >
        {children}
      </IntlProvider>
    </LocaleContext.Provider>
  );
};

export default LocaleContextProvider;
