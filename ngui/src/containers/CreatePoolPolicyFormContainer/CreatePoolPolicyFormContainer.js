import React, { useEffect, useState } from "react";
import { useDispatch } from "react-redux";
import { useNavigate } from "react-router-dom";
import { getAvailablePools, RESTAPI } from "api";
import { GET_AVAILABLE_POOLS } from "api/restapi/actionTypes";
import CreatePoolPolicyForm from "components/CreatePoolPolicyForm";
import { useApiState } from "hooks/useApiState";
import { useConstraints } from "hooks/useConstraints";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import PoolPolicyService from "services/PoolPolicyService";
import { RESOURCE_LIFECYCLE } from "urls";
import { checkError } from "utils/api";
import { getIntersection, isEmpty as isEmptyArray } from "utils/arrays";

const CreatePoolPolicyFormContainer = () => {
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const allowedConstraints = useConstraints();

  const { useCreateGlobalPoolPolicy } = PoolPolicyService();
  const { create: createPoolPolicy, isLoading: isCreatePoolPolicyLoading } = useCreateGlobalPoolPolicy();

  const redirect = () => navigate(RESOURCE_LIFECYCLE);

  const onSubmit = ({ poolId, limit, type }) => {
    createPoolPolicy(
      {
        poolId,
        params: {
          limit,
          type
        }
      },
      {
        onSuccess: () => redirect()
      }
    );
  };

  const { organizationId } = useOrganizationInfo();

  const [hasPermissionsToCreatePolicy, setHasPermissionsToCreatePolicy] = useState(true);
  const [pools, setPools] = useState([]);

  const { isLoading: isGetAvailablePoolsLoading, isDataReady: isGetAvailablePoolsDataReady } = useApiState(GET_AVAILABLE_POOLS);

  useEffect(() => {
    dispatch((_, getState) => {
      dispatch(
        getAvailablePools(organizationId, {
          permission: ["MANAGE_POOLS"]
        })
      )
        .then(() => checkError(GET_AVAILABLE_POOLS, getState()))
        .then(() => {
          const { pools: poolsData } = getState()[RESTAPI][GET_AVAILABLE_POOLS];

          if (isEmptyArray(poolsData)) {
            setHasPermissionsToCreatePolicy(false);
          } else {
            setPools(
              poolsData.filter(({ policies = [] }) => {
                const existingPolPoliciesTypes = policies.map((policy) => policy.type);

                if (getIntersection(existingPolPoliciesTypes, allowedConstraints).length === allowedConstraints.length) {
                  return false;
                }

                return true;
              })
            );
          }
        });
    });
  }, [allowedConstraints, dispatch, organizationId]);

  return (
    <CreatePoolPolicyForm
      isGetLoading={isGetAvailablePoolsLoading}
      isDataReady={isGetAvailablePoolsDataReady}
      isSubmitLoading={isCreatePoolPolicyLoading}
      pools={pools}
      hasPermissionsToCreatePolicy={hasPermissionsToCreatePolicy}
      onSubmit={onSubmit}
      onCancel={redirect}
    />
  );
};

export default CreatePoolPolicyFormContainer;
