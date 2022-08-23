import React, { useState, useEffect } from "react";
import { useDispatch } from "react-redux";
import { getTrafficExpenses } from "api";
import { GET_TRAFFIC_EXPENSES } from "api/restapi/actionTypes";
import TrafficExpenses from "components/TrafficExpenses";
import { useApiData } from "hooks/useApiData";
import { useApiState } from "hooks/useApiState";
import { useDefaultDateRange } from "hooks/useDefaultDateRange";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { DATE_RANGE_TYPE } from "utils/constants";
import { updateQueryParams } from "utils/network";

const TrafficExpensesContainer = () => {
  const dispatch = useDispatch();
  const { organizationId } = useOrganizationInfo();

  const [startDateTimestamp, endDateTimestamp] = useDefaultDateRange(DATE_RANGE_TYPE.EXPENSES);

  const [requestParams, setRequestParams] = useState({
    startDate: startDateTimestamp,
    endDate: endDateTimestamp
  });

  const { isDataReady, shouldInvoke } = useApiState(GET_TRAFFIC_EXPENSES, { ...requestParams, organizationId });

  useEffect(() => {
    if (shouldInvoke) {
      dispatch(getTrafficExpenses(organizationId, requestParams));
    }
  }, [dispatch, shouldInvoke, organizationId, requestParams]);

  const {
    apiData: { expenses = {} }
  } = useApiData(GET_TRAFFIC_EXPENSES);

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
    <TrafficExpenses
      isLoading={!isDataReady}
      expenses={expenses}
      applyFilter={applyFilter}
      startDateTimestamp={requestParams.startDate}
      endDateTimestamp={requestParams.endDate}
    />
  );
};

export default TrafficExpensesContainer;
