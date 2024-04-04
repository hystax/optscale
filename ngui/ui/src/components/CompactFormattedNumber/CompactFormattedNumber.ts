import { FormatNumberOptions, useIntl } from "react-intl";

type FormatterFunctionType = (value: number, options: FormatNumberOptions) => string;

type CompactFormattedNumberProps = {
  value: number;
  format?: string;
  maximumFractionDigits?: number;
};

export const formatCompactNumber =
  (formatter: FormatterFunctionType) =>
  ({ value, format, maximumFractionDigits }: CompactFormattedNumberProps) => {
    const formattedNumber = formatter(value, { notation: "compact", format, maximumFractionDigits });
    return formattedNumber.endsWith("K")
      ? `${formattedNumber.slice(0, formattedNumber.length - 1)}${formattedNumber
          .slice(formattedNumber.length - 1)
          .toLocaleLowerCase()}`
      : formattedNumber;
  };

const CompactFormattedNumber = ({ value, format, maximumFractionDigits }: CompactFormattedNumberProps) => {
  const intl = useIntl();

  return formatCompactNumber(intl.formatNumber)({ value, format, maximumFractionDigits });
};

export default CompactFormattedNumber;
