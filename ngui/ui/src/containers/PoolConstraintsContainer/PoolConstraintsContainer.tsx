import { useEffect } from "react";
import { useDispatch } from "react-redux";
import { getPoolPolicies } from "api";
import { GET_POOL_POLICIES } from "api/restapi/actionTypes";
import PoolConstraints from "components/PoolConstraints";
import { useApiData } from "hooks/useApiData";
import { useApiState } from "hooks/useApiState";

const PoolConstraintsContainer = ({ poolId }) => {
  const dispatch = useDispatch();

  const {
    apiData: { poolPolicies = [] }
  } = useApiData(GET_POOL_POLICIES);
  const { isLoading, shouldInvoke } = useApiState(GET_POOL_POLICIES, { poolId });

  useEffect(() => {
    if (shouldInvoke) {
      dispatch(getPoolPolicies(poolId));
    }
  }, [poolId, shouldInvoke, dispatch]);

  return <PoolConstraints isLoading={isLoading} policies={poolPolicies} poolId={poolId} />;
};

export default PoolConstraintsContainer;
