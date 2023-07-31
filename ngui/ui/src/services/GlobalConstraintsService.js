import { useEffect } from "react";
import { useDispatch } from "react-redux";
import {
  getGlobalPoolPolicies,
  getGlobalResourceConstraints,
  RESTAPI,
  getPoolAllowedActions,
  getResourceAllowedActions
} from "api";
import { GET_POOL_ALLOWED_ACTIONS, GET_RESOURCE_ALLOWED_ACTIONS } from "api/auth/actionTypes";
import { GET_GLOBAL_POOL_POLICIES, GET_GLOBAL_RESOURCE_CONSTRAINTS } from "api/restapi/actionTypes";
import { useApiData } from "hooks/useApiData";
import { useApiState } from "hooks/useApiState";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { checkError } from "utils/api";

const params = { details: true };

const useGetPoolPolicies = () => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();

  const { isLoading: isGetGlobalPoolPoliciesLoading, shouldInvoke } = useApiState(GET_GLOBAL_POOL_POLICIES, {
    organizationId,
    ...params
  });

  const { isLoading: isGetPoolAllowedActionsLoading } = useApiState(GET_POOL_ALLOWED_ACTIONS);

  const { apiData: policies = [] } = useApiData(GET_GLOBAL_POOL_POLICIES, []);

  useEffect(() => {
    if (shouldInvoke) {
      dispatch((_, getState) => {
        dispatch(getGlobalPoolPolicies(organizationId, params))
          .then(() => checkError(GET_GLOBAL_POOL_POLICIES, getState()))
          .then(() => {
            const resourcePolicies = getState()?.[RESTAPI]?.[GET_GLOBAL_POOL_POLICIES] ?? [];

            const poolIds = [...new Set(resourcePolicies.map(({ pool_id: poolId }) => poolId))];

            dispatch(getPoolAllowedActions(poolIds));
          });
      });
    }
  }, [shouldInvoke, dispatch, organizationId]);

  return { isLoading: isGetGlobalPoolPoliciesLoading || isGetPoolAllowedActionsLoading, policies };
};

const useGetResourceConstraints = () => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();

  const { isLoading: isGetGlobalResourceConstraintsLoading, shouldInvoke } = useApiState(GET_GLOBAL_RESOURCE_CONSTRAINTS, {
    organizationId,
    ...params
  });
  const { apiData: constraints } = useApiData(GET_GLOBAL_RESOURCE_CONSTRAINTS, []);

  const { isLoading: isGetResourceAllowedActionsLoading } = useApiState(GET_RESOURCE_ALLOWED_ACTIONS);

  useEffect(() => {
    if (shouldInvoke) {
      dispatch((_, getState) => {
        dispatch(getGlobalResourceConstraints(organizationId, params))
          .then(() => checkError(GET_GLOBAL_RESOURCE_CONSTRAINTS, getState()))
          .then(() => {
            const resourceConstraints = getState()?.[RESTAPI]?.[GET_GLOBAL_RESOURCE_CONSTRAINTS] ?? [];

            const resourceIds = [...new Set(resourceConstraints.map(({ resource_id: resourceId }) => resourceId))];

            dispatch(getResourceAllowedActions(resourceIds));
          });
      });
    }
  }, [shouldInvoke, dispatch, organizationId]);

  return { isLoading: isGetGlobalResourceConstraintsLoading || isGetResourceAllowedActionsLoading, constraints };
};

function GlobalConstraintsService() {
  return { useGetPoolPolicies, useGetResourceConstraints };
}

export default GlobalConstraintsService;
