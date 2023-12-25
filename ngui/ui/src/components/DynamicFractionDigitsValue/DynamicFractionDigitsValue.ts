import { useCallback } from "react";
import { useIntl } from "react-intl";
import { formatCompactNumber } from "components/CompactFormattedNumber";

export const useFormatDynamicFractionDigitsValue = () => {
  const intl = useIntl();

  return useCallback(
    ({ value, maximumFractionDigits = 2, notation }) => {
      const props = {
        maximumFractionDigits
      };

      if (notation === "compact") {
        return formatCompactNumber(intl.formatNumber)({
          value,
          ...props
        });
      }

      return intl.formatNumber(value, props);
    },
    [intl]
  );
};

const DynamicFractionDigitsValue = ({ value, maximumFractionDigits = 2, notation }) => {
  const format = useFormatDynamicFractionDigitsValue();

  return format({ value, maximumFractionDigits, notation });
};

export default DynamicFractionDigitsValue;
