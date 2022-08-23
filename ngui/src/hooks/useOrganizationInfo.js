import { GET_ORGANIZATIONS } from "api/restapi/actionTypes";
import { SCOPE_ID } from "containers/OrganizationSelectorContainer/reducer";
import { useApiData } from "hooks/useApiData";
import { useRootData } from "hooks/useRootData";

// TODO: Try to get a currency symbol from localization
const getCurrencySymbol = (currency) => {
  switch (currency) {
    case "RUB":
      return "₽";
    case "EUR":
      return "€";
    case "BRL":
      return "R$";
    case "CAD":
      return "CA$";
    default:
      return "$";
  }
};

const getActiveOrganization = (organizationId, organizations) => {
  // 1. Take organization by id from storage
  // 2. Take first organization from storage
  // 3. Take empty object

  let organization = organizations.find((org) => org.id === organizationId);

  if (!organization) {
    [organization = {}] = organizations;
  }

  return organization;
};

export const useOrganizationInfo = () => {
  const { rootData: organizationId } = useRootData(SCOPE_ID);

  const {
    apiData: { organizations = [] }
  } = useApiData(GET_ORGANIZATIONS);

  const {
    pool_id: organizationPoolId,
    name,
    is_demo: isDemo = false,
    id: newOrganizationId,
    currency
  } = getActiveOrganization(organizationId, organizations);

  return {
    // Return either new or existed organization id from the storage
    // The existed organization id will be returned in cases when there is not organizations in the store, e.g on the login page
    organizationId: newOrganizationId || organizationId,
    name,
    organizationPoolId,
    isDemo,
    currency,
    currencySymbol: getCurrencySymbol(currency)
  };
};
