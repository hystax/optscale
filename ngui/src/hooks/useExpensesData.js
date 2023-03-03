import { useApiData } from "hooks/useApiData";
import { useReactiveDefaultDateRange } from "hooks/useReactiveDefaultDateRange";
import { DATE_RANGE_TYPE, FILTER_BY } from "utils/constants";
import { getQueryParams } from "utils/network";

export const useExpensesData = (label) => {
  const {
    apiData: { expenses = {} }
  } = useApiData(label);

  const queryParams = getQueryParams();

  const { [FILTER_BY]: filterBy } = queryParams;

  const [startDateTimestamp, endDateTimestamp] = useReactiveDefaultDateRange(DATE_RANGE_TYPE.EXPENSES);

  const {
    name,
    total = 0,
    previous_total: previousTotal = 0,
    breakdown = {},
    [filterBy]: filteredBreakdown = [],
    id: poolId,
    type
  } = expenses;

  return {
    filterBy,
    startDateTimestamp,
    endDateTimestamp,
    name,
    total,
    previousTotal,
    breakdown,
    filteredBreakdown,
    poolId,
    dataSourceType: type
  };
};
