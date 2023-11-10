import { useFormatOrganizationCurrency } from "hooks/useFormatOrganizationCurrency";

const FormattedOrganizationCurrency = ({ currencyCode }) => {
  const formatOrganizationCurrency = useFormatOrganizationCurrency();

  return formatOrganizationCurrency(currencyCode);
};

export default FormattedOrganizationCurrency;
