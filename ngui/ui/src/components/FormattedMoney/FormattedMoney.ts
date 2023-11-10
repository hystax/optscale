import { FORMATTED_MONEY_TYPES } from "utils/constants";
import { useMoneyFormatter } from "./useMoneyFormatter";

/**
 * See {@link https://datatrendstech.atlassian.net/wiki/spaces/NGUI/pages/1969651789/Money+format|Money format} for more information on when to use the different types
 */
const FormattedMoney = ({ value, format, type = FORMATTED_MONEY_TYPES.COMMON, ...rest }) => {
  const formatter = useMoneyFormatter();

  return formatter(type, value, { format, ...rest });
};

export default FormattedMoney;
