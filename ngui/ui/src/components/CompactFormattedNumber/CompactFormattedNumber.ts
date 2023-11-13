import { useIntl } from "react-intl";

export const formatCompactNumber =
  (formatter) =>
  ({ value, format, maximumFractionDigits }) => {
    const formattedNumber = formatter(value, { notation: "compact", format, maximumFractionDigits });
    return formattedNumber.endsWith("K")
      ? `${formattedNumber.slice(0, formattedNumber.length - 1)}${formattedNumber
          .slice(formattedNumber.length - 1)
          .toLocaleLowerCase()}`
      : formattedNumber;
  };

const CompactFormattedNumber = ({ value, format, maximumFractionDigits }) => {
  const intl = useIntl();

  return formatCompactNumber(intl.formatNumber)({ value, format, maximumFractionDigits });
};

export default CompactFormattedNumber;
