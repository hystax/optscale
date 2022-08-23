import React, { useEffect } from "react";
import PropTypes from "prop-types";
import { useDispatch, useSelector } from "react-redux";
import { getAvailablePools } from "api";
import { GET_AVAILABLE_POOLS } from "api/restapi/actionTypes";
import AvailablePoolSelector from "components/AvailablePoolSelector";
import { useApiData } from "hooks/useApiData";
import { useApiState } from "hooks/useApiState";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { setPoolId } from "reducers/resources/actionCreators";

const AvailablePoolSelectorContainer = ({ splitGroup, permission, error, helperText, dataTestId }) => {
  const { organizationId } = useOrganizationInfo();

  const resourcesState = useSelector((state) => state.resources) || {};
  const { [splitGroup]: { poolId = "" } = {} } = resourcesState;

  const dispatch = useDispatch();

  const { isLoading, shouldInvoke } = useApiState(GET_AVAILABLE_POOLS, { permission, organizationId });

  useEffect(() => {
    if (shouldInvoke) {
      dispatch(getAvailablePools(organizationId, { permission }));
    }
  }, [shouldInvoke, dispatch, organizationId, permission]);

  const onChange = (newPoolId) => {
    dispatch(setPoolId(newPoolId, splitGroup));
  };

  const {
    apiData: { pools = [] }
  } = useApiData(GET_AVAILABLE_POOLS);

  return (
    <AvailablePoolSelector
      error={error}
      helperText={helperText}
      pools={pools}
      selected={poolId}
      onChange={onChange}
      isLoading={isLoading}
      dataTestId={dataTestId}
    />
  );
};

AvailablePoolSelectorContainer.propTypes = {
  splitGroup: PropTypes.string.isRequired,
  permission: PropTypes.array.isRequired,
  error: PropTypes.bool,
  helperText: PropTypes.string,
  dataTestId: PropTypes.string
};

export default AvailablePoolSelectorContainer;
