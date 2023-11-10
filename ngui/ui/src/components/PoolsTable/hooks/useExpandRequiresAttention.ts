import { useDispatch } from "react-redux";
import { getRecursiveParent } from "utils/arrays";
import { setExpandedRows } from "../actionCreators";
import { isCostOverLimit, isForecastOverLimit } from "../utils";

const useExpandRequiresAttention = (rootPool) => {
  const dispatch = useDispatch();
  const expandRequiresAttentionHandler = () => {
    const pools = [rootPool, ...(rootPool.children || [])];

    const expandArray = pools
      .filter(({ limit, cost, forecast }) => isCostOverLimit({ limit, cost }) || isForecastOverLimit({ limit, forecast }))
      .flatMap((p) => [...getRecursiveParent(p, pools, "id")], []);

    const uniqueExpandArray = [...new Set(expandArray)];

    dispatch(setExpandedRows(uniqueExpandArray));
  };

  return expandRequiresAttentionHandler;
};

export default useExpandRequiresAttention;
