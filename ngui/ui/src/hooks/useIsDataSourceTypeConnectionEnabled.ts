import { NEBIUS_ACCOUNT } from "utils/constants";
import { useIsNebiusConnectionEnabled } from "./useIsNebiusConnectionEnabled";

export const useIsDataSourceTypeConnectionEnabled = () => {
  const isNebiusConnectionEnabled = useIsNebiusConnectionEnabled();

  const isConnectionTypeEnabled = (connectionType) =>
    ({
      [NEBIUS_ACCOUNT]: isNebiusConnectionEnabled
    })[connectionType] ??
    /**
     * Connection is enabled by default
     */
    true;

  return (connectionType) => isConnectionTypeEnabled(connectionType);
};
