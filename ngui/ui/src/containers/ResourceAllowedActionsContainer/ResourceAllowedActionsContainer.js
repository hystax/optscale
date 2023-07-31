import { useEffect } from "react";
import PropTypes from "prop-types";
import { useDispatch } from "react-redux";
import { getResourceAllowedActions } from "api";
import { GET_RESOURCE_ALLOWED_ACTIONS } from "api/auth/actionTypes";
import { useApiState } from "hooks/useApiState";

const ResourceAllowedActionsContainer = ({ resourceId, children }) => {
  const { shouldInvoke, isLoading } = useApiState(GET_RESOURCE_ALLOWED_ACTIONS, resourceId);
  const dispatch = useDispatch();

  useEffect(() => {
    if (shouldInvoke) {
      dispatch(getResourceAllowedActions(resourceId));
    }
  }, [shouldInvoke, dispatch, resourceId]);

  return children({ isGetPermissionsLoading: isLoading });
};

ResourceAllowedActionsContainer.propTypes = {
  resourceId: PropTypes.string.isRequired,
  children: PropTypes.func.isRequired
};

export default ResourceAllowedActionsContainer;
