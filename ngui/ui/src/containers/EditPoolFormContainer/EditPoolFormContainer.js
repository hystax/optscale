import React, { useEffect, useState } from "react";
import PropTypes from "prop-types";
import { useDispatch } from "react-redux";
import { useNavigate } from "react-router-dom";
import { updatePool, getPoolOwners, getPool, RESTAPI } from "api";
import { UPDATE_POOL, GET_POOL_OWNERS, GET_POOL } from "api/restapi/actionTypes";
import PoolFormWrapper from "components/PoolFormWrapper";
import { useApiData } from "hooks/useApiData";
import { useApiState } from "hooks/useApiState";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { getPoolUrl } from "urls";
import { isError } from "utils/api";
import { isEmpty } from "utils/arrays";

const EditPoolFormContainer = ({ poolId }) => {
  const dispatch = useDispatch();
  const navigate = useNavigate();

  const { organizationId } = useOrganizationInfo();

  const [isFormDataLoading, setIsFormDataLoading] = useState(false);
  const [parentPoolId, setParentPoolId] = useState(null);
  const [hasSubPools, setHasSubPools] = useState(false);

  const [defaultValues, setDefaultValues] = useState({
    name: "",
    limit: 0,
    type: "",
    defaultOwnerId: "",
    autoExtension: false
  });

  useEffect(() => {
    dispatch((_, getState) => {
      setIsFormDataLoading(true);
      dispatch(getPool(poolId))
        .then(() => {
          if (isError(GET_POOL, getState())) {
            return Promise.reject();
          }
          const pool = getState()?.[RESTAPI]?.[GET_POOL]?.pool ?? {};
          const {
            name: poolName,
            limit: limitAmount,
            default_owner_id: defaultResourceOwnerId,
            purpose: type,
            parent_id: parentId,
            children = []
          } = pool || {};

          setParentPoolId(parentId);
          setHasSubPools(!isEmpty(children));

          setDefaultValues((currentDefaultValues) => ({
            ...currentDefaultValues,
            name: poolName,
            limit: limitAmount,
            type,
            defaultOwnerId: defaultResourceOwnerId || "",
            autoExtension: false
          }));
          return dispatch(getPoolOwners(poolId))
            .catch(() => {})
            .finally(() => {
              setIsFormDataLoading(false);
            });
        })
        .catch(() => {});
    });
  }, [dispatch, organizationId, poolId]);

  // Get pool owners
  const {
    apiData: { poolOwners = [] }
  } = useApiData(GET_POOL_OWNERS);

  // Update pool
  const { isLoading: isUpdateLoading } = useApiState(UPDATE_POOL);

  // Redirect on success and cancel
  const redirect = () => navigate(getPoolUrl(poolId));

  const onSubmit = ({ name, limit, defaultOwnerId, autoExtension, type: poolType }) => {
    const defaultParameters = {
      id: poolId,
      parentId: parentPoolId,
      limit: parseFloat(limit),
      defaultOwnerId
    };
    return dispatch((_, getState) => {
      dispatch(
        updatePool(
          parentPoolId
            ? {
                ...defaultParameters,
                name,
                type: poolType,
                autoExtension
              }
            : defaultParameters
        )
      ).then(() => {
        if (!isError(UPDATE_POOL, getState())) {
          redirect();
        }
      });
    });
  };

  return (
    <PoolFormWrapper
      poolId={poolId}
      parentPoolId={parentPoolId}
      defaultValues={defaultValues}
      owners={poolOwners}
      hasSubPools={hasSubPools}
      onSubmit={onSubmit}
      onCancel={redirect}
      isLoadingProps={{
        isPoolOwnersLoading: isFormDataLoading,
        isGetPoolLoading: isFormDataLoading,
        isEditLoading: isUpdateLoading || isFormDataLoading
      }}
    />
  );
};

EditPoolFormContainer.propTypes = {
  poolId: PropTypes.string.isRequired
};

export default EditPoolFormContainer;
