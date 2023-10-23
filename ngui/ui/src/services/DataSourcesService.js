import { useEffect } from "react";
import { useDispatch } from "react-redux";
import { getDataSources, updateDataSource, disconnectDataSource as disconnectDataSourceApi } from "api";
import { DELETE_DATA_SOURCE, GET_DATA_SOURCES, UPDATE_DATA_SOURCE } from "api/restapi/actionTypes";
import { useApiData } from "hooks/useApiData";
import { useApiState } from "hooks/useApiState";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { checkError } from "utils/api";
import { ENVIRONMENT } from "utils/constants";

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

const useDisconnectDataSource = () => {
  const dispatch = useDispatch();

  const { isLoading } = useApiState(DELETE_DATA_SOURCE);

  const disconnectDataSource = (id) =>
    new Promise((resolve, reject) => {
      dispatch((_, getState) => {
        dispatch(disconnectDataSourceApi(id))
          .then(() => checkError(DELETE_DATA_SOURCE, getState()))
          .then(() => resolve())
          .catch(() => reject());
      });
    });

  return { disconnectDataSource, isLoading };
};

const useIsLastDataSource = () => {
  const {
    apiData: { cloudAccounts = [] }
  } = useApiData(GET_DATA_SOURCES);

  return cloudAccounts.filter(({ type }) => type !== ENVIRONMENT).length === 1;
};

function DataSourcesService() {
  return { useGetDataSources, useUpdateDataSource, useDisconnectDataSource, useIsLastDataSource };
}

export default DataSourcesService;
