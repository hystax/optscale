import React, { useState, useEffect } from "react";
import { useDispatch } from "react-redux";
import { getRegionExpenses } from "api";
import { GET_REGION_EXPENSES } from "api/restapi/actionTypes";
import RegionExpenses from "components/RegionExpenses";
import { useApiData } from "hooks/useApiData";
import { useApiState } from "hooks/useApiState";
import { useDefaultDateRange } from "hooks/useDefaultDateRange";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { DATE_RANGE_TYPE } from "utils/constants";
import { updateQueryParams } from "utils/network";

const RegionExpensesContainer = () => {
  const dispatch = useDispatch();
  const { organizationId } = useOrganizationInfo();

  const [startDateTimestamp, endDateTimestamp] = useDefaultDateRange(DATE_RANGE_TYPE.EXPENSES);

  const [requestParams, setRequestParams] = useState({
    startDate: startDateTimestamp,
    endDate: endDateTimestamp
  });

  const { isLoading, shouldInvoke } = useApiState(GET_REGION_EXPENSES, { ...requestParams, organizationId });

  useEffect(() => {
    if (shouldInvoke) {
      dispatch(getRegionExpenses(organizationId, requestParams));
    }
  }, [dispatch, shouldInvoke, organizationId, requestParams]);

  const {
    apiData: { expenses = {} }
  } = useApiData(GET_REGION_EXPENSES);

  useEffect(() => {
    updateQueryParams(requestParams);
  }, [requestParams]);

  const applyFilter = ({ startDate, endDate }) => {
    const params = {
      ...requestParams,
      startDate,
      endDate
    };
    setRequestParams(params);
  };

  return (
    <RegionExpenses
      isLoading={isLoading}
      expenses={expenses}
      applyFilter={applyFilter}
      startDateTimestamp={startDateTimestamp}
      endDateTimestamp={endDateTimestamp}
    />
  );
};

export default RegionExpensesContainer;
