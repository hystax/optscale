import { useEffect } from "react";
import { useDispatch } from "react-redux";
import { getEnvironments, RESTAPI, getResourceAllowedActions } from "api";
import { GET_RESOURCE_ALLOWED_ACTIONS } from "api/auth/actionTypes";
import { GET_ENVIRONMENTS } from "api/restapi/actionTypes";
import { useApiData } from "hooks/useApiData";
import { useApiState } from "hooks/useApiState";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { isError } from "utils/api";

export const useGet = () => {
  const dispatch = useDispatch();
  const { organizationId } = useOrganizationInfo();
  const { apiData: environments } = useApiData(GET_ENVIRONMENTS, []);

  const { isLoading: isGetEnvironmentsLoading, shouldInvoke } = useApiState(GET_ENVIRONMENTS, organizationId);
  const { isLoading: isGetResourceAllowedActionsLoading } = useApiState(GET_RESOURCE_ALLOWED_ACTIONS);

  useEffect(() => {
    if (shouldInvoke) {
      dispatch((_, getState) => {
        dispatch(getEnvironments(organizationId)).then(() => {
          if (!isError(GET_ENVIRONMENTS, getState())) {
            const storedEnvironments = getState()?.[RESTAPI]?.[GET_ENVIRONMENTS] ?? [];
            const resourceIds = storedEnvironments.map((environment) => environment.id);

            dispatch(getResourceAllowedActions(resourceIds));
          }
        });
      });
    }
  }, [dispatch, organizationId, shouldInvoke]);

  return { isGetEnvironmentsLoading, isGetResourceAllowedActionsLoading, environments };
};

function EnvironmentsService() {
  return { useGet };
}

export default EnvironmentsService;
