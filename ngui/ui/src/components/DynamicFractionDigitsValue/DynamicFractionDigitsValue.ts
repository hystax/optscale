import { useCallback } from "react";
import { useIntl } from "react-intl";
import { formatCompactNumber } from "components/CompactFormattedNumber";

type DynamicFractionDigitsValueProps = {
  value: number;
  maximumFractionDigits?: number;
  notation?: "compact";
};

type FormatFunctionType = (props: DynamicFractionDigitsValueProps) => string;

export const useFormatDynamicFractionDigitsValue = (): FormatFunctionType => {
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

const DynamicFractionDigitsValue = ({ value, maximumFractionDigits = 2, notation }: DynamicFractionDigitsValueProps) => {
  const format = useFormatDynamicFractionDigitsValue();

  return format({ value, maximumFractionDigits, notation });
};

export default DynamicFractionDigitsValue;
