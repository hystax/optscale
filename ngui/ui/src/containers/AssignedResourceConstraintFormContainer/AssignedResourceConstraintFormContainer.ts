import { useEffect } from "react";
import { useDispatch } from "react-redux";
import { getPoolAllowedActions } from "api";
import { GET_POOL_ALLOWED_ACTIONS } from "api/auth/actionTypes";
import { useIsAllowed } from "hooks/useAllowedActions";
import { useApiState } from "hooks/useApiState";
import { SCOPE_TYPES } from "utils/constants";

const AssignedResourceConstraintFormContainer = ({ poolId, children }) => {
  const { shouldInvoke: shouldInvokerGetPoolAllowedActions, isLoading: isGetPoolAllowedActionsLoading } = useApiState(
    GET_POOL_ALLOWED_ACTIONS,
    poolId
  );
  const dispatch = useDispatch();

  useEffect(() => {
    if (shouldInvokerGetPoolAllowedActions) {
      dispatch(getPoolAllowedActions(poolId));
    }
  }, [shouldInvokerGetPoolAllowedActions, dispatch, poolId]);

  const canEdit = useIsAllowed({ entityType: SCOPE_TYPES.POOL, entityId: poolId, requiredActions: ["MANAGE_POOLS"] });

  return children({ isGetPermissionsLoading: isGetPoolAllowedActionsLoading, canEdit });
};

export default AssignedResourceConstraintFormContainer;
