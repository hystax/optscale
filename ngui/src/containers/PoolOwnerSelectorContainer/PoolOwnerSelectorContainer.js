import React, { useEffect } from "react";
import PropTypes from "prop-types";
import { useDispatch, useSelector } from "react-redux";
import { getPoolOwners } from "api";
import { GET_POOL_OWNERS, GET_AVAILABLE_POOLS } from "api/restapi/actionTypes";
import PoolOwnerSelector from "components/PoolOwnerSelector";
import { useApiData } from "hooks/useApiData";
import { useApiState } from "hooks/useApiState";
import { setOwnerId } from "reducers/resources/actionCreators";

const PoolOwnerSelectorContainer = ({ splitGroup, excludeMyself, error, helperText, dataTestId }) => {
  const resourcesState = useSelector((state) => state.resources);
  const { [splitGroup]: { poolId = "", ownerId: poolOwnerId = "" } = {} } = resourcesState;

  const { isLoading: isGetPoolOwnersLoading, shouldInvoke } = useApiState(GET_POOL_OWNERS, { poolId, excludeMyself });
  const { isLoading: isGetAvailablePoolsLoading } = useApiState(GET_AVAILABLE_POOLS);
  const isLoading = isGetPoolOwnersLoading || isGetAvailablePoolsLoading;

  const dispatch = useDispatch();

  useEffect(() => {
    if (poolId && shouldInvoke) {
      dispatch(getPoolOwners(poolId, excludeMyself));
    }
  }, [shouldInvoke, dispatch, poolId, excludeMyself]);

  const onChange = (newPoolOwnerId) => {
    dispatch(setOwnerId(newPoolOwnerId, splitGroup));
  };

  const {
    apiData: { poolOwners = [] }
  } = useApiData(GET_POOL_OWNERS);

  return (
    <PoolOwnerSelector
      error={error}
      helperText={helperText}
      owners={poolOwners}
      selected={poolOwnerId}
      onChange={onChange}
      isLoading={isLoading}
      dataTestId={dataTestId}
    />
  );
};

PoolOwnerSelectorContainer.propTypes = {
  splitGroup: PropTypes.string.isRequired,
  excludeMyself: PropTypes.bool,
  error: PropTypes.bool,
  helperText: PropTypes.string,
  dataTestId: PropTypes.string
};

export default PoolOwnerSelectorContainer;
