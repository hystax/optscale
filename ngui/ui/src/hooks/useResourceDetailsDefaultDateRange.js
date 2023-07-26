import { useEffect } from "react";
import { DATE_RANGE_TYPE, DATE_RANGE_FILTERS } from "utils/constants";
import { removeQueryParam, getQueryParams } from "utils/network";
import { useReactiveDefaultDateRange } from "./useReactiveDefaultDateRange";

const useDateRange = ({ lastSeen, firstSeen, syntheticDateFilter }) => {
  const [startDateTimestamp, endDateTimestamp] = useReactiveDefaultDateRange(DATE_RANGE_TYPE.RESOURCES);

  const startDateValue = syntheticDateFilter === DATE_RANGE_FILTERS.ALL && firstSeen ? firstSeen : startDateTimestamp;
  const endDateValue = syntheticDateFilter === DATE_RANGE_FILTERS.ALL && lastSeen ? lastSeen : endDateTimestamp;

  return [startDateValue, endDateValue];
};

const useSyntheticDateFilter = () => {
  const { syntheticDateFilter } = getQueryParams();

  useEffect(() => {
    if (syntheticDateFilter) {
      removeQueryParam("syntheticDateFilter");
    }
  }, [syntheticDateFilter]);

  return syntheticDateFilter;
};

export const useResourceDetailsDefaultDateRange = ({ lastSeen, firstSeen }) => {
  const syntheticDateFilter = useSyntheticDateFilter();

  const [startDateTimestamp, endDateTimestamp] = useDateRange({
    lastSeen,
    firstSeen,
    syntheticDateFilter
  });

  return [startDateTimestamp, endDateTimestamp];
};
