import { useEffect, useState } from "react";
import { updateQueryParams } from "utils/network";

export const useExpensesBreakdownRequestParams = ({ filterBy, startDateTimestamp, endDateTimestamp }) => {
  const [requestParams, setRequestParams] = useState({
    filterBy,
    startDate: startDateTimestamp,
    endDate: endDateTimestamp
  });

  useEffect(() => {
    setRequestParams((curr) => ({ ...curr, filterBy }));
  }, [filterBy]);

  useEffect(() => {
    updateQueryParams(requestParams);
  }, [requestParams]);

  const applyFilter = ({ startDate: msStartDate, endDate: msEndDate }) => {
    const params = {
      ...requestParams,
      startDate: msStartDate,
      endDate: msEndDate
    };
    setRequestParams(params);
  };

  const updateFilter = (newFilterBy) => {
    if (newFilterBy !== requestParams.filterBy) {
      const params = { ...requestParams, filterBy: newFilterBy };
      setRequestParams(params);
    }
  };

  return [requestParams, applyFilter, updateFilter];
};
