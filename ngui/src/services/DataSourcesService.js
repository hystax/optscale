import { useEffect } from "react";
import { useDispatch } from "react-redux";
import { getCloudAccounts, updateCloudAccount } from "api";
import { GET_CLOUD_ACCOUNTS, UPDATE_CLOUD_ACCOUNT } from "api/restapi/actionTypes";
import { useApiData } from "hooks/useApiData";
import { useApiState } from "hooks/useApiState";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { checkError } from "utils/api";

export const useGetDataSources = () => {
  const dispatch = useDispatch();
  const { organizationId } = useOrganizationInfo();

  const {
    apiData: { cloudAccounts = [] }
  } = useApiData(GET_CLOUD_ACCOUNTS);

  const { isLoading, shouldInvoke } = useApiState(GET_CLOUD_ACCOUNTS, organizationId);

  useEffect(() => {
    if (shouldInvoke) {
      dispatch(getCloudAccounts(organizationId));
    }
  }, [dispatch, organizationId, shouldInvoke]);

  return { isGetDataSourceLoading: isLoading, dataSources: cloudAccounts };
};

const useUpdateDataSource = () => {
  const dispatch = useDispatch();

  const { isLoading } = useApiState(UPDATE_CLOUD_ACCOUNT);

  const onUpdate = (id, params) =>
    new Promise((resolve, reject) => {
      dispatch((_, getState) => {
        dispatch(updateCloudAccount(id, params))
          .then(() => checkError(UPDATE_CLOUD_ACCOUNT, getState()))
          .then(() => resolve())
          .catch(() => reject());
      });
    });

  return { onUpdate, isLoading };
};

function DataSourcesService() {
  return { useGetDataSources, useUpdateDataSource };
}

export default DataSourcesService;
