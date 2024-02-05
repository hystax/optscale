import { useCallback } from "react";
import { useTheme } from "@mui/material/styles";
import { useRootData } from "hooks/useRootData";
import { isCostOverLimit, isForecastOverLimit } from "utils/pools";
import { EXPANDED_POOL_ROWS } from "../reducer";

const checkPoolAndSubpools = (parent, subPools, isExpanded = false) => {
  // testing parent
  const { limit, cost, forecast } = parent;
  const checks = {
    exceededExpenses: isCostOverLimit({ limit, cost }),
    exceededForecast: isForecastOverLimit({ limit, forecast })
  };
  if (checks.exceededExpenses || isExpanded) {
    return checks;
  }

  subPools.every((pool) => {
    if (pool.parent_id === parent.id) {
      const childCheck = checkPoolAndSubpools(pool, subPools);

      checks.exceededExpenses = checks.exceededExpenses || childCheck.exceededExpenses;
      checks.exceededForecast = checks.exceededForecast || childCheck.exceededForecast;
      // found exceededExpenses child, no need to iterate more
      if (checks.exceededExpenses) {
        return false;
      }
    }
    return true;
  });

  return checks;
};

const noAttentionStyle = { borderLeft: "4px solid transparent" };
const useGetRowStyle = (pools) => {
  const theme = useTheme();
  const { rootData: expandedPoolIds = [] } = useRootData(EXPANDED_POOL_ROWS);
  const getRowStyle = useCallback(
    (original) => {
      const { hasLimit, id } = original;

      if (!hasLimit) {
        return noAttentionStyle;
      }

      const getChecks = () => {
        const isExpanded = expandedPoolIds.includes(id);

        return checkPoolAndSubpools(original, pools.children, isExpanded);
      };

      const check = getChecks();

      if (check.exceededExpenses) {
        return {
          borderLeft: `4px solid ${theme.palette.error.main}`
        };
      }
      if (check.exceededForecast) {
        return {
          borderLeft: `4px solid ${theme.palette.warning.main}`
        };
      }
      return noAttentionStyle;
    },
    [theme, expandedPoolIds, pools]
  );

  return getRowStyle;
};

export default useGetRowStyle;
