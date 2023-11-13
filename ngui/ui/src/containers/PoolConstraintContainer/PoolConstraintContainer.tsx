import { useDispatch } from "react-redux";
import { createPoolPolicy, updatePoolPolicyLimit, updatePoolPolicyActivity } from "api";
import { CREATE_POOL_POLICY, UPDATE_POOL_POLICY_LIMIT, UPDATE_POOL_POLICY_ACTIVITY } from "api/restapi/actionTypes";
import PoolConstraintForm from "components/PoolConstraintForm";
import { useApiState } from "hooks/useApiState";
import { isError } from "utils/api";

const PoolConstraintContainer = ({ poolId, policy, isLoading, policyType }) => {
  const dispatch = useDispatch();

  const { isLoading: createIsLoading } = useApiState(CREATE_POOL_POLICY);
  const { isLoading: updateIsLoading, entityId } = useApiState(UPDATE_POOL_POLICY_LIMIT);
  const { isLoading: isUpdateActivityLoading, entityId: updateActivityEntityId } = useApiState(UPDATE_POOL_POLICY_ACTIVITY);

  const create = ({ limit, type }, { onSuccess }) =>
    dispatch((_, getState) => {
      dispatch(createPoolPolicy(poolId, { limit, type })).then(() => {
        if (!isError(CREATE_POOL_POLICY, getState()) && typeof onSuccess === "function") {
          onSuccess();
        }
      });
    });
  const update = ({ limit, policyId }, { onSuccess }) =>
    dispatch((_, getState) => {
      dispatch(updatePoolPolicyLimit(policyId, limit)).then(() => {
        if (!isError(UPDATE_POOL_POLICY_LIMIT, getState()) && typeof onSuccess === "function") {
          onSuccess();
        }
      });
    });
  const updateActivity = (policyId, active) => dispatch(updatePoolPolicyActivity(policyId, active));

  return (
    <PoolConstraintForm
      poolId={poolId}
      update={update}
      create={create}
      updateActivity={updateActivity}
      policy={policy}
      isLoading={isLoading}
      policyType={policyType}
      isLoadingProps={{
        isGetDataLoading: isLoading,
        isUpdateLoading: policy?.id === entityId && updateIsLoading,
        isUpdateActivityLoading: policy?.id === updateActivityEntityId && isUpdateActivityLoading,
        isCreateLoading: createIsLoading
      }}
    />
  );
};

export default PoolConstraintContainer;
