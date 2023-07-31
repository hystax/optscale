import { useEffect } from "react";
import { useDispatch } from "react-redux";
import { getDataSources, updateDataSource } from "api";
import { GET_DATA_SOURCES, UPDATE_DATA_SOURCE } from "api/restapi/actionTypes";
import { useApiData } from "hooks/useApiData";
import { useApiState } from "hooks/useApiState";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { checkError } from "utils/api";

export const useGetDataSources = () => {
  const dispatch = useDispatch();
  const { organizationId } = useOrganizationInfo();

  const {
    apiData: { cloudAccounts = [] }
  } = useApiData(GET_DATA_SOURCES);

  const { isLoading, shouldInvoke } = useApiState(GET_DATA_SOURCES, organizationId);

  useEffect(() => {
    if (shouldInvoke) {
      dispatch(getDataSources(organizationId));
    }
  }, [dispatch, organizationId, shouldInvoke]);

  return { isGetDataSourceLoading: isLoading, dataSources: cloudAccounts };
};

const useUpdateDataSource = () => {
  const dispatch = useDispatch();

  const { isLoading } = useApiState(UPDATE_DATA_SOURCE);

  const onUpdate = (id, params) =>
    new Promise((resolve, reject) => {
      dispatch((_, getState) => {
        dispatch(updateDataSource(id, params))
          .then(() => checkError(UPDATE_DATA_SOURCE, getState()))
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
