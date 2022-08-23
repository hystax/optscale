import { useEffect } from "react";
import { useDispatch } from "react-redux";
import { getJiraOrganizationStatus } from "api";
import { GET_JIRA_ORGANIZATION_STATUS } from "api/jira_bus/actionTypes";
import { useApiData } from "hooks/useApiData";
import { useApiState } from "hooks/useApiState";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";

export const useGet = () => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();

  const { shouldInvoke, isLoading } = useApiState(GET_JIRA_ORGANIZATION_STATUS, organizationId);

  const {
    apiData: { connected_tenants: connectedTenants = [] }
  } = useApiData(GET_JIRA_ORGANIZATION_STATUS);

  useEffect(() => {
    if (shouldInvoke) {
      dispatch(getJiraOrganizationStatus(organizationId));
    }
  }, [dispatch, organizationId, shouldInvoke]);

  return { isLoading, connectedTenants };
};

function JiraOrganizationStatusService() {
  return { useGet };
}

export default JiraOrganizationStatusService;
