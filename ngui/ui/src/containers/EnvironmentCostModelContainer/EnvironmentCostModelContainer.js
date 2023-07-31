import React, { useEffect } from "react";
import PropTypes from "prop-types";
import { useDispatch } from "react-redux";
import { getResourceCostModel } from "api";
import { GET_RESOURCE_COST_MODEL } from "api/restapi/actionTypes";
import EnvironmentCostModel from "components/EnvironmentCostModel";
import { useApiData } from "hooks/useApiData";
import { useApiState } from "hooks/useApiState";

// TODO: isGetPermissionsLoading can be defined here, the API can be invoked here,
// Data is not invoked from ResourceAllowedActionsContainer, reconsider the approach
const EnvironmentCostModelContainer = ({ resourceId, isGetPermissionsLoading = false }) => {
  const dispatch = useDispatch();
  const { shouldInvoke, isLoading: isGetResourceCostModelLoading } = useApiState(GET_RESOURCE_COST_MODEL, resourceId);

  useEffect(() => {
    if (shouldInvoke) {
      dispatch(getResourceCostModel(resourceId));
    }
  }, [dispatch, resourceId, shouldInvoke]);

  const {
    apiData: { value: { hourly_cost: hourlyPrice = 0 } = {} }
  } = useApiData(GET_RESOURCE_COST_MODEL);

  return (
    <EnvironmentCostModel
      resourceId={resourceId}
      hourlyPrice={hourlyPrice}
      isLoadingProps={{ isGetResourceCostModelLoading, isGetPermissionsLoading }}
    />
  );
};

EnvironmentCostModelContainer.propTypes = {
  resourceId: PropTypes.string.isRequired,
  isGetPermissionsLoading: PropTypes.bool
};

export default EnvironmentCostModelContainer;
