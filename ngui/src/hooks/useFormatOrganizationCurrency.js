import { useIntl } from "react-intl";
import localeManager from "translations/localeManager";

export const useFormatOrganizationCurrency = () => {
  const intl = useIntl();

  return (currencyCode) =>
    intl.formatMessage(
      {
        id: "value(parenthesisValue)"
      },
      {
        value: intl.formatMessage(
          { id: "value - value" },
          {
            value1: currencyCode,
            value2: intl.formatMessage({ id: currencyCode })
          }
        ),
        parenthesisValue: localeManager.getCurrencySymbol(currencyCode)
      }
    );
};
