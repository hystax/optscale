import { shallowEqual, useSelector } from "react-redux";

export const useIsLoading = (labels) => {
  const isLoadingStates = useSelector((state) => labels.map((lbl) => state.api?.[lbl]?.isLoading ?? false), shallowEqual);
  return isLoadingStates.some((loading) => loading === true);
};
