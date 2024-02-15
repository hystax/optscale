import { useEffect } from "react";
import { useDispatch } from "react-redux";
import { useInitialMount } from "hooks/useInitialMount";
import { useRootData } from "hooks/useRootData";
import { useSyncQueryParamWithState } from "hooks/useSyncQueryParamWithState";
import { POOL_QUERY_PARAM_NAME } from "urls";
import { getRecursiveParent } from "utils/arrays";
import { setExpandedRows } from "../actionCreators";
import { EXPANDED_POOL_ROWS } from "../reducer";

const useHoverableRows = ({ onClick, rootPool, isGetPoolDataReady }) => {
  const dispatch = useDispatch();
  const [selectedPool, setSelectedPool] = useSyncQueryParamWithState({
    queryParamName: POOL_QUERY_PARAM_NAME,
    defaultValue: ""
  });

  const handleRowClick = ({ id }) => {
    setSelectedPool(id);
    onClick(id);
  };
  const isSelectedRow = ({ id }) => id === selectedPool;
  const { isInitialMount, setIsInitialMount } = useInitialMount();
  const { rootData: expandedPoolIds = [] } = useRootData(EXPANDED_POOL_ROWS);

  // opening rows to make selected pool visible on initial load
  useEffect(() => {
    if (!isGetPoolDataReady || !isInitialMount) {
      return;
    }
    const pools = [rootPool, ...(rootPool.children || [])];
    const selectedPoolInfo = pools.find(({ id }) => id === selectedPool);

    if (selectedPoolInfo) {
      const expandedMerged = [...expandedPoolIds, ...getRecursiveParent(selectedPoolInfo, pools, "id")];
      const expandedUnique = [...new Set(expandedMerged)];
      dispatch(setExpandedRows(expandedUnique));
    }

    setIsInitialMount(false);
  }, [isGetPoolDataReady, dispatch, rootPool, selectedPool, isInitialMount, setIsInitialMount, expandedPoolIds]);

  return { isSelectedRow, handleRowClick };
};
export default useHoverableRows;
