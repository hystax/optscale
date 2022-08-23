import { useEffect } from "react";
import { useDispatch } from "react-redux";
import { getAvailablePools, deletePool as deletePoolAction } from "api";
import { DELETE_POOL, GET_AVAILABLE_POOLS } from "api/restapi/actionTypes";
import { useApiData } from "hooks/useApiData";
import { useApiState } from "hooks/useApiState";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { rejectOnError } from "utils/api";

export const useGetAvailablePools = () => {
  const dispatch = useDispatch();
  const { organizationId } = useOrganizationInfo();

  const {
    apiData: { pools = [] }
  } = useApiData(GET_AVAILABLE_POOLS);

  const { isLoading, shouldInvoke, isDataReady } = useApiState(GET_AVAILABLE_POOLS, { organizationId });

  useEffect(() => {
    if (shouldInvoke) {
      dispatch(getAvailablePools(organizationId));
    }
  }, [dispatch, organizationId, shouldInvoke]);

  return { data: pools, isLoading, isDataReady };
};

export const useGetAvailablePoolsOnce = () => {
  const dispatch = useDispatch();
  const { organizationId } = useOrganizationInfo();

  const {
    apiData: { pools = [] }
  } = useApiData(GET_AVAILABLE_POOLS);

  const { isLoading, isDataReady } = useApiState(GET_AVAILABLE_POOLS, { organizationId });

  useEffect(() => {
    dispatch(getAvailablePools(organizationId));
  }, [dispatch, organizationId]);

  return { data: pools, isLoading, isDataReady };
};

const useDelete = () => {
  const dispatch = useDispatch();

  const { isLoading } = useApiState(DELETE_POOL);

  const deletePool = (poolId, onSuccess) => {
    dispatch(deletePoolAction(poolId))
      .then(rejectOnError(dispatch, DELETE_POOL))
      .then(() => {
        if (typeof onSuccess === "function") {
          onSuccess();
        }
      });
  };

  return { deletePool, isDeletePoolLoading: isLoading };
};

function PoolsService() {
  return { useGetAvailablePools, useGetAvailablePoolsOnce, useDelete };
}

export default PoolsService;
