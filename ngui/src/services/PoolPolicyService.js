import { useDispatch } from "react-redux";
import {
  updateGlobalPoolPolicyLimit,
  updateGlobalPoolPolicyActivity,
  updatePoolPolicyActivity,
  createGlobalPoolPolicy,
  updatePoolPolicyLimit,
  createPoolPolicy
} from "api";
import {
  CREATE_GLOBAL_POOL_POLICY,
  CREATE_POOL_POLICY,
  UPDATE_GLOBAL_POOL_POLICY_ACTIVITY,
  UPDATE_GLOBAL_POOL_POLICY_LIMIT,
  UPDATE_POOL_POLICY_ACTIVITY,
  UPDATE_POOL_POLICY_LIMIT
} from "api/restapi/actionTypes";
import { useApiState } from "hooks/useApiState";
import { checkError } from "utils/api";

const useUpdateGlobalPoolPolicyLimit = () => {
  const dispatch = useDispatch();

  const update = ({ policyId, limit }, { onSuccess, onError } = {}) => {
    dispatch((__, getState) => {
      dispatch(updateGlobalPoolPolicyLimit(policyId, limit))
        .then(() => checkError(UPDATE_GLOBAL_POOL_POLICY_LIMIT, getState()))
        .then(() => {
          if (typeof onSuccess === "function") {
            onSuccess();
          }
        })
        .catch(() => {
          if (typeof onError === "function") {
            onError();
          }
        });
    });
  };

  return { update };
};

const useUpdatePoolPolicyLimit = () => {
  const dispatch = useDispatch();

  const { isLoading, entityId } = useApiState(UPDATE_POOL_POLICY_LIMIT);

  const update = ({ policyId, limit }, { onSuccess, onError } = {}) => {
    dispatch((__, getState) => {
      dispatch(updatePoolPolicyLimit(policyId, limit))
        .then(() => checkError(UPDATE_POOL_POLICY_LIMIT, getState()))
        .then(() => {
          if (typeof onSuccess === "function") {
            onSuccess();
          }
        })
        .catch(() => {
          if (typeof onError === "function") {
            onError();
          }
        });
    });
  };

  return { update, isLoading, entityId };
};

const useUpdateGlobalPoolPolicyActivity = () => {
  const dispatch = useDispatch();

  const update = ({ policyId, isActive }, { onSuccess, onError } = {}) => {
    dispatch((_, getState) => {
      dispatch(updateGlobalPoolPolicyActivity(policyId, isActive))
        .then(() => checkError(UPDATE_GLOBAL_POOL_POLICY_ACTIVITY, getState()))
        .then(() => {
          if (typeof onSuccess === "function") {
            onSuccess();
          }
        })
        .catch(() => {
          if (typeof onError === "function") {
            onError();
          }
        });
    });
  };

  return { update };
};

const useUpdatePoolPolicyActivity = () => {
  const dispatch = useDispatch();

  const { isLoading, entityId } = useApiState(UPDATE_POOL_POLICY_ACTIVITY);

  const update = ({ policyId, isActive }, { onSuccess, onError } = {}) => {
    dispatch((_, getState) => {
      dispatch(updatePoolPolicyActivity(policyId, isActive))
        .then(() => checkError(UPDATE_POOL_POLICY_ACTIVITY, getState()))
        .then(() => {
          if (typeof onSuccess === "function") {
            onSuccess();
          }
        })
        .catch(() => {
          if (typeof onError === "function") {
            onError();
          }
        });
    });
  };

  return { update, isLoading, entityId };
};

const useCreateGlobalPoolPolicy = () => {
  const dispatch = useDispatch();

  const { isLoading } = useApiState(CREATE_GLOBAL_POOL_POLICY);

  const create = ({ poolId, params }, { onSuccess, onError } = {}) => {
    dispatch((_, getState) => {
      dispatch(createGlobalPoolPolicy(poolId, params))
        .then(() => checkError(CREATE_GLOBAL_POOL_POLICY, getState()))
        .then(() => {
          if (typeof onSuccess === "function") {
            onSuccess();
          }
        })
        .catch(() => {
          if (typeof onError === "function") {
            onError();
          }
        });
    });
  };

  return {
    isLoading,
    create
  };
};

const useCreatePoolPolicy = () => {
  const dispatch = useDispatch();

  const { isLoading } = useApiState(CREATE_POOL_POLICY);

  const create = ({ poolId, params }, { onSuccess, onError } = {}) => {
    dispatch((_, getState) => {
      dispatch(createPoolPolicy(poolId, params))
        .then(() => checkError(CREATE_POOL_POLICY, getState()))
        .then(() => {
          if (typeof onSuccess === "function") {
            onSuccess();
          }
        })
        .catch(() => {
          if (typeof onError === "function") {
            onError();
          }
        });
    });
  };

  return {
    isLoading,
    create
  };
};

function PoolPolicyService() {
  return {
    useUpdateGlobalPoolPolicyLimit,
    useUpdatePoolPolicyLimit,
    useUpdateGlobalPoolPolicyActivity,
    useUpdatePoolPolicyActivity,
    useCreateGlobalPoolPolicy,
    useCreatePoolPolicy
  };
}

export default PoolPolicyService;
