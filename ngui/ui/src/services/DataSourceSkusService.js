import { useEffect } from "react";
import { useDispatch } from "react-redux";
import { getDataSourceSkus, updateDataSourceSku } from "api";
import { GET_DATASOURCE_SKUS, UPDATE_DATASOURCE_SKU } from "api/restapi/actionTypes";
import { useApiData } from "hooks/useApiData";
import { useApiState } from "hooks/useApiState";
import { isError } from "utils/api";

export const useGet = (dataSourceId) => {
  const dispatch = useDispatch();

  const { isLoading, shouldInvoke } = useApiState(GET_DATASOURCE_SKUS, dataSourceId);

  const { apiData: data } = useApiData(GET_DATASOURCE_SKUS);

  useEffect(() => {
    if (shouldInvoke) {
      dispatch(getDataSourceSkus(dataSourceId));
    }
  }, [dataSourceId, dispatch, shouldInvoke]);

  const skus = Object.entries(data?.value ?? {}).reduce((result, [sku, cost]) => [...result, { sku, cost }], []);

  return { isLoading, skus, usedSkus: data?.used_skus ?? [] };
};

const useUpdateDataSourceSku = () => {
  const dispatch = useDispatch();

  const { isLoading } = useApiState(UPDATE_DATASOURCE_SKU);

  const onUpdate = (dataSourceId, value) =>
    new Promise((resolve, reject) => {
      dispatch((_, getState) => {
        dispatch(updateDataSourceSku(dataSourceId, value)).then(() => {
          if (!isError(UPDATE_DATASOURCE_SKU, getState())) {
            return resolve();
          }
          return reject();
        });
      });
    });

  return { onUpdate, isLoading };
};

function DataSourceSkusService() {
  return { useGet, useUpdateDataSourceSku };
}

export default DataSourceSkusService;
