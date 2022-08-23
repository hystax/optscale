import React, { useEffect } from "react";
import { useDispatch } from "react-redux";
import { getDetailedCloudAccounts, getPool } from "api";
import { GET_DETAILED_CLOUD_ACCOUNTS, GET_CLOUD_ACCOUNTS, GET_POOL } from "api/restapi/actionTypes";
import CloudAccountsOverview from "components/CloudAccountsOverview";
import { useApiData } from "hooks/useApiData";
import { useApiState } from "hooks/useApiState";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";

const GetCloudAccountsContainer = () => {
  const {
    apiData: { cloudAccounts = [] }
  } = useApiData(GET_CLOUD_ACCOUNTS);

  const { organizationPoolId, organizationId } = useOrganizationInfo();

  const { isLoading: isGetDetailedCloudAccountsLoading, shouldInvoke: shouldInvokeGetDetailedCloudAccounts } = useApiState(
    GET_DETAILED_CLOUD_ACCOUNTS,
    organizationId
  );

  const dispatch = useDispatch();

  useEffect(() => {
    if (shouldInvokeGetDetailedCloudAccounts) {
      dispatch(getDetailedCloudAccounts(organizationId));
    }
  }, [shouldInvokeGetDetailedCloudAccounts, dispatch, organizationId]);

  const {
    apiData: { pool: { limit: organizationLimit = 0 } = {} }
  } = useApiData(GET_POOL);

  const { isLoading: isGetPoolLoading, shouldInvoke: shouldInvokeGetPool } = useApiState(GET_POOL, {
    poolId: organizationPoolId
  });

  useEffect(() => {
    if (organizationPoolId && shouldInvokeGetPool) {
      dispatch(getPool(organizationPoolId));
    }
  }, [shouldInvokeGetPool, dispatch, organizationPoolId]);

  return (
    <CloudAccountsOverview
      isLoading={isGetDetailedCloudAccountsLoading || isGetPoolLoading}
      cloudAccounts={cloudAccounts}
      organizationLimit={organizationLimit}
    />
  );
};

export default GetCloudAccountsContainer;
