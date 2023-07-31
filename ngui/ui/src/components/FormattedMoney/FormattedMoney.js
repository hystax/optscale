import PropTypes from "prop-types";
import { FORMATTED_MONEY_TYPES } from "utils/constants";
import { useMoneyFormatter } from "./useMoneyFormatter";

/**
 * See {@link https://datatrendstech.atlassian.net/wiki/spaces/NGUI/pages/1969651789/Money+format|Money format} for more information on when to use the different types
 */
const FormattedMoney = ({ value, format, type = FORMATTED_MONEY_TYPES.COMMON, ...rest }) => {
  const formatter = useMoneyFormatter();

  return formatter(type, value, { format, ...rest });
};

FormattedMoney.propTypes = {
  value: (props, propName, componentName) => {
    const value = props[propName];
    if (value === undefined) {
      return new Error(`Invalid prop \`${propName}\` (value = ${value}) supplied to \`${componentName}\`. Validation failed.`);
    }
    return undefined;
  },
  type: PropTypes.oneOf(Object.values(FORMATTED_MONEY_TYPES)),
  format: PropTypes.string
};

export default FormattedMoney;
