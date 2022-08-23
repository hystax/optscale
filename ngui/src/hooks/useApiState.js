import { useSelector } from "react-redux";
import { hashParams } from "api/utils";
import { isTtlExpired } from "utils/api";

export const useApiState = (targetAction, requestParams) => {
  const isLoading = useSelector((state) => state.api?.[targetAction]?.isLoading ?? false);

  const entityId = useSelector((state) => state.api?.[targetAction]?.entityId ?? "");

  const timestamp = useSelector((state) => state.api?.[targetAction]?.timestamp ?? 0);

  const hash = useSelector((state) => state.api?.[targetAction]?.hash ?? 0);

  const paramsUpdated = requestParams !== undefined && hashParams(requestParams) !== hash;

  const ttlExpired = isTtlExpired(timestamp);

  const shouldInvoke = paramsUpdated || ttlExpired;

  return { isLoading, shouldInvoke, entityId, isDataReady: !isLoading && !shouldInvoke };
};
