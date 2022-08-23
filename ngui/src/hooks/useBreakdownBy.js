import { useEffect, useState } from "react";
import { RESOURCES_EXPENSES_DAILY_BREAKDOWN_BY, RESOURCES_EXPENSES_DAILY_BREAKDOWN_BY_VALUES } from "utils/constants";
import { getQueryParams, updateQueryParams } from "utils/network";

export const useBreakdownBy = ({ queryParamName }) => {
  const [breakdownBy, setBreakdownBy] = useState(() => {
    const { [queryParamName]: breakdownByQueryParameter } = getQueryParams();

    return RESOURCES_EXPENSES_DAILY_BREAKDOWN_BY_VALUES.includes(breakdownByQueryParameter)
      ? breakdownByQueryParameter
      : RESOURCES_EXPENSES_DAILY_BREAKDOWN_BY.SERVICE_NAME;
  });

  const onBreakdownByChange = (newBreakdownBy) => {
    setBreakdownBy(newBreakdownBy);
  };

  useEffect(() => {
    updateQueryParams({ [queryParamName]: breakdownBy });
  }, [breakdownBy, queryParamName]);

  return [breakdownBy, onBreakdownByChange];
};
