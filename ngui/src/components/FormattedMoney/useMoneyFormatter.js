import { useIntl } from "react-intl";
import { formatApproximatelyZero } from "components/ApproximatelyZero";
import { formatCompactNumber } from "components/CompactFormattedNumber";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { usePolyfillIntlNumberFormat } from "hooks/usePolyfillIntlNumberFormat";
import { ONE_CENT, FORMATTED_MONEY_TYPES } from "utils/constants";

const COMPACT_VALUE_THRESHOLD = 1000;

const formatCompactMoney =
  (formatter) =>
  ({ value, format }) =>
    formatCompactNumber(formatter)({ value, format: `${format}Compact` });

const formatCommon =
  (formatter) =>
  ({ value, format, absoluteValue }) =>
    absoluteValue < ONE_CENT ? formatApproximatelyZero(formatter)({ format }) : formatter(value, { format });

const formatCompact =
  (formatter) =>
  ({ value, format, absoluteValue }) => {
    if (absoluteValue >= COMPACT_VALUE_THRESHOLD) {
      return formatCompactMoney(formatter)({ value, format });
    }
    return absoluteValue < ONE_CENT ? formatApproximatelyZero(formatter)({ format }) : formatter(value, { format });
  };

const formatTiny =
  (formatter) =>
  ({ value, format, maximumFractionDigits = 4 }) =>
    formatter(value, { format, maximumFractionDigits });

const formatTinyCompact =
  (formatter) =>
  ({ value, format, maximumFractionDigits = 4 }) => {
    if (Math.abs(value) >= COMPACT_VALUE_THRESHOLD) {
      return formatCompactMoney(formatter)({ value, format });
    }

    return formatter(value, { format, maximumFractionDigits });
  };

export const useMoneyFormatter = () => {
  const { currency = "USD" } = useOrganizationInfo();

  const intl = useIntl();

  const isPolyfilled = usePolyfillIntlNumberFormat();

  return (type, value, { format, ...rest } = {}) => {
    if (!isPolyfilled) {
      return "";
    }

    const calculatedFormat = format || currency;

    if (!value) {
      return intl.formatNumber(0, { format: calculatedFormat });
    }

    const formatter = {
      [FORMATTED_MONEY_TYPES.COMMON]: formatCommon,
      [FORMATTED_MONEY_TYPES.COMPACT]: formatCompact,
      [FORMATTED_MONEY_TYPES.TINY_COMPACT]: formatTinyCompact,
      [FORMATTED_MONEY_TYPES.TINY]: formatTiny
    }[type];

    return formatter(intl.formatNumber)({ value, absoluteValue: Math.abs(value), format: calculatedFormat, ...rest });
  };
};
