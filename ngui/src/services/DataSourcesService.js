import { useEffect } from "react";
import { useDispatch } from "react-redux";
import { getCloudAccounts } from "api";
import { GET_CLOUD_ACCOUNTS } from "api/restapi/actionTypes";
import { useApiData } from "hooks/useApiData";
import { useApiState } from "hooks/useApiState";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";

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

function DataSourcesService() {
  return { useGetDataSources };
}

export default DataSourcesService;
