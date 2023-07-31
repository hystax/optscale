import PropTypes from "prop-types";
import { useFormatOrganizationCurrency } from "hooks/useFormatOrganizationCurrency";
import { currencyCodes } from "utils/currency";

const FormattedOrganizationCurrency = ({ currencyCode }) => {
  const formatOrganizationCurrency = useFormatOrganizationCurrency();

  return formatOrganizationCurrency(currencyCode);
};

FormattedOrganizationCurrency.propTypes = {
  currencyCode: PropTypes.oneOf(currencyCodes).isRequired
};

export default FormattedOrganizationCurrency;
