import { useMemo } from "react";
import { CONSTRAINTS, TOTAL_EXPENSE_LIMIT } from "utils/constraints";
import { useOrganizationFeatures } from "./useOrganizationFeatures";

export const useConstraints = () => {
  const { total_expense_limit_enabled: totalExpenseLimitEnabled = 0 } = useOrganizationFeatures();

  return useMemo(
    () => CONSTRAINTS.filter((type) => type !== TOTAL_EXPENSE_LIMIT || totalExpenseLimitEnabled),
    [totalExpenseLimitEnabled]
  );
};
