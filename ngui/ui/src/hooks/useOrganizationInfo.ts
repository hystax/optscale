import { useSelector } from "react-redux";
import { SCOPE_ID } from "containers/OrganizationSelectorContainer/reducer";
import localeManager from "translations/localeManager";
import { useOrganizations } from "./coreData/useOrganizations";

export const useCurrentOrganization = (organizations = []) => {
  // Take current/active organization ID from storage
  const currentOrganizationId = useSelector((state) => state[SCOPE_ID]);

  // If there is no organization found by that ID, take the first one from storage
  const {
    id: organizationId,
    pool_id: organizationPoolId,
    name: organizationName,
    is_demo: isDemo = false,
    currency = "USD",
    disabled = false,
  } = organizations.find((org) => org.id === currentOrganizationId) ?? organizations?.[0] ?? {};

  return {
    organizationId,
    name: organizationName,
    organizationPoolId,
    isDemo,
    isInactive: disabled,
    currency,
    currencySymbol: currency ? localeManager.getCurrencySymbol(currency) : undefined,
  };
};

export const useOrganizationInfo = () => {
  const organizations = useOrganizations();

  const currentOrganization = useCurrentOrganization(organizations);

  return currentOrganization;
};
