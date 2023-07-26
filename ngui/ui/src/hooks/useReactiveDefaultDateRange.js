import { useMemo } from "react";
import { RANGE_DATES } from "containers/RangePickerFormContainer/reducer";
import { useRootData } from "hooks/useRootData";
import { getCurrentMonthRange } from "utils/datetime";
import { useReactiveSearchParams } from "./useReactiveSearchParams";

const DATE_RANGE_SEARCH_PARAMS = ["startDate", "endDate"];

/**
 * Calculates and returns default date range in seconds.
 *
 * @description
 * The order of operations
 * 1. Take URL query parameters
 * 2. Take values from storage by key
 * 3. Take default date range (current month)
 *
 * @param {string} rangeDatesKey Storage address key
 * @returns {Array of numbers} Start and end dates
 *
 */
export const useReactiveDefaultDateRange = (rangeDatesKey, isUtc = true) => {
  const { rootData: storageRangeDates = {} } = useRootData(RANGE_DATES, (result = {}) => result[rangeDatesKey]);

  const { startDate: sStartDateQueryParam, endDate: sEndDateQueryParam } = useReactiveSearchParams(DATE_RANGE_SEARCH_PARAMS);

  const { startOfMonth: defaultStartDate, today: defaultEndDate } = getCurrentMonthRange(isUtc);

  const sStartDateTimestamp = sStartDateQueryParam || storageRangeDates.startDate || defaultStartDate;
  const sEndDateTimestamp = sEndDateQueryParam || storageRangeDates.endDate || defaultEndDate;

  const numberSStartDateTimestamp = Number(sStartDateTimestamp);
  const numberSEndDateTimestamp = Number(sEndDateTimestamp);

  const range = useMemo(
    () => [numberSStartDateTimestamp, numberSEndDateTimestamp],
    [numberSStartDateTimestamp, numberSEndDateTimestamp]
  );

  return range;
};
