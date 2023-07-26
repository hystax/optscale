import { useEffect } from "react";
import { useDispatch } from "react-redux";
import { getOrganizationLimitHits } from "api";
import { GET_ORGANIZATION_LIMIT_HITS } from "api/restapi/actionTypes";
import { useApiData } from "hooks/useApiData";
import { useApiState } from "hooks/useApiState";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";

export const useGet = (constraintId) => {
  const { organizationId } = useOrganizationInfo();

  const { isLoading, shouldInvoke } = useApiState(GET_ORGANIZATION_LIMIT_HITS, { organizationId, constraintId });

  const dispatch = useDispatch();

  useEffect(() => {
    if (shouldInvoke) {
      dispatch(getOrganizationLimitHits(organizationId, { constraintId }));
    }
  }, [constraintId, dispatch, organizationId, shouldInvoke]);

  const { apiData: { organization_limit_hits: data = [] } = {} } = useApiData(GET_ORGANIZATION_LIMIT_HITS);

  return { isLoading, data };
};

function OrganizationsLimitHitsService() {
  return { useGet };
}

export default OrganizationsLimitHitsService;
