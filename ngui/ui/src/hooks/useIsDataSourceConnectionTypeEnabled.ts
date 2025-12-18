import { useCallback } from "react";
import { CONNECTION_TYPES } from "utils/constants";
import { ObjectValues } from "utils/types";
import { useIsNebiusConnectionEnabled } from "./useIsNebiusConnectionEnabled";

type ConnectionType = ObjectValues<typeof CONNECTION_TYPES>;

export const useIsDataSourceConnectionTypeEnabled = () => {
  const isNebiusConnectionEnabled = useIsNebiusConnectionEnabled();

  return useCallback(
    (type: ConnectionType) =>
      ({
        [CONNECTION_TYPES.AWS_ROLE]: true,
        [CONNECTION_TYPES.AWS_ROOT]: true,
        [CONNECTION_TYPES.AWS_LINKED]: true,
        [CONNECTION_TYPES.AZURE_TENANT]: true,
        [CONNECTION_TYPES.AZURE_SUBSCRIPTION]: true,
        [CONNECTION_TYPES.GCP_TENANT]: true,
        [CONNECTION_TYPES.GCP_PROJECT]: true,
        [CONNECTION_TYPES.ALIBABA]: true,
        [CONNECTION_TYPES.DATABRICKS]: true,
        [CONNECTION_TYPES.KUBERNETES]: true,
        [CONNECTION_TYPES.NEBIUS]: isNebiusConnectionEnabled
      })[type] ?? false,
    [isNebiusConnectionEnabled]
  );
};
