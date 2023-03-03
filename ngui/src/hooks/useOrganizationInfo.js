import { GET_ORGANIZATIONS } from "api/restapi/actionTypes";
import { SCOPE_ID } from "containers/OrganizationSelectorContainer/reducer";
import { useApiData } from "hooks/useApiData";
import { useRootData } from "hooks/useRootData";
import localeManager from "translations/localeManager";

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
  // TODO: need to check setScopeId function, which is not being called
  // after authorization, so old organization id is still persisted,
  // even after login with another user (with another organizations set)
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
    organizationId: newOrganizationId,
    name,
    organizationPoolId,
    isDemo,
    currency,
    currencySymbol: currency ? localeManager.getCurrencySymbol(currency) : undefined
  };
};
