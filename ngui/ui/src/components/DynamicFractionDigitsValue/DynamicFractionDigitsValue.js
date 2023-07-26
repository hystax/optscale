import PropTypes from "prop-types";
import { useIntl } from "react-intl";
import { formatCompactNumber } from "components/CompactFormattedNumber";

export const useFormatDynamicFractionDigitsValue = () => {
  const intl = useIntl();

  return ({ value, maximumFractionDigits = 2, notation }) => {
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
  };
};

const DynamicFractionDigitsValue = ({ value, maximumFractionDigits = 2, notation }) => {
  const format = useFormatDynamicFractionDigitsValue();

  return format({ value, maximumFractionDigits, notation });
};

DynamicFractionDigitsValue.propTypes = {
  value: PropTypes.number.isRequired,
  maximumFractionDigits: PropTypes.number,
  notation: PropTypes.string
};

export default DynamicFractionDigitsValue;
