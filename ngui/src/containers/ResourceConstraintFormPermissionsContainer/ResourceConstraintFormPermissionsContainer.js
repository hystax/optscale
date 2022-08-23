import { useEffect } from "react";
import PropTypes from "prop-types";
import { useDispatch } from "react-redux";
import { getResourceAllowedActions } from "api";
import { GET_RESOURCE_ALLOWED_ACTIONS } from "api/auth/actionTypes";
import { useApiState } from "hooks/useApiState";
import { useIsAllowedToManageResourceConstraint } from "hooks/useResourceConstraintPermissions";

const ResourceConstraintFormPermissionsContainer = ({ resourceId, children, employeeId }) => {
  const { shouldInvoke: shouldInvokerGetResourceAllowedActions, isLoading: isGetResourceAllowedActionsLoading } = useApiState(
    GET_RESOURCE_ALLOWED_ACTIONS,
    resourceId
  );
  const dispatch = useDispatch();

  useEffect(() => {
    if (shouldInvokerGetResourceAllowedActions && employeeId) {
      dispatch(getResourceAllowedActions(resourceId));
    }
  }, [shouldInvokerGetResourceAllowedActions, dispatch, resourceId, employeeId]);

  const canEdit = useIsAllowedToManageResourceConstraint(employeeId, resourceId);

  return children({ isGetPermissionsLoading: isGetResourceAllowedActionsLoading, canEdit });
};

ResourceConstraintFormPermissionsContainer.propTypes = {
  resourceId: PropTypes.string.isRequired,
  children: PropTypes.func.isRequired,
  employeeId: PropTypes.string
};

export default ResourceConstraintFormPermissionsContainer;
