import { useMemo } from "react";
import { GET_DATA_SOURCES } from "api/restapi/actionTypes";
import { AWS_CNR } from "utils/constants";
import { useApiData } from "./useApiData";

export const useAwsDataSources = () => {
  const {
    apiData: { cloudAccounts: dataSources = [] }
  } = useApiData(GET_DATA_SOURCES);

  return useMemo(() => dataSources.filter(({ type }) => type === AWS_CNR), [dataSources]);
};
