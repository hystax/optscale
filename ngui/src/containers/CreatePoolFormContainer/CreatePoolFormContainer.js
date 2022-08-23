import React, { useEffect, useCallback } from "react";
import PropTypes from "prop-types";
import { useDispatch } from "react-redux";
import { useNavigate } from "react-router-dom";
import { createPool, getPool } from "api";
import { GET_POOL, CREATE_POOL } from "api/restapi/actionTypes";
import PoolFormWrapper from "components/PoolFormWrapper";
import { useApiData } from "hooks/useApiData";
import { useApiState } from "hooks/useApiState";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { getPoolUrl } from "urls";
import { isError } from "utils/api";

const CreatePoolFormContainer = ({ parentPoolId }) => {
  const navigate = useNavigate();
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();

  const {
    apiData: { pool: { name: parentPoolName } = {} }
  } = useApiData(GET_POOL);

  const { isLoading: isGetParentPoolLoading, shouldInvoke } = useApiState(GET_POOL, {
    poolId: parentPoolId
  });

  useEffect(() => {
    if (shouldInvoke) {
      dispatch(getPool(parentPoolId));
    }
  }, [shouldInvoke, dispatch, parentPoolId]);

  const { isLoading: isCreatePoolLoading } = useApiState(CREATE_POOL);

  const redirect = useCallback(() => navigate(getPoolUrl(parentPoolId)), [parentPoolId, navigate]);

  const onSubmit = ({ name, limit, type, autoExtension }) => {
    dispatch((_, getState) => {
      dispatch(
        createPool(organizationId, { parentId: parentPoolId, name, autoExtension, limit: parseFloat(limit), type })
      ).then(() => {
        if (!isError(CREATE_POOL, getState())) {
          return redirect();
        }
        return undefined;
      });
    });
  };

  return (
    <PoolFormWrapper
      isLoadingProps={{
        isCreateLoading: isCreatePoolLoading,
        isGetParentPoolLoading
      }}
      parentPoolName={parentPoolName}
      parentPoolId={parentPoolId}
      onCancel={redirect}
      onSubmit={onSubmit}
    />
  );
};

CreatePoolFormContainer.propTypes = {
  parentPoolId: PropTypes.string
};

export default CreatePoolFormContainer;
