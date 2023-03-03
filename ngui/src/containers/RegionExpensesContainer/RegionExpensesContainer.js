import React, { useEffect } from "react";
import { useDispatch } from "react-redux";
import { getRegionExpenses } from "api";
import { GET_REGION_EXPENSES } from "api/restapi/actionTypes";
import RegionExpenses from "components/RegionExpenses";
import { useApiData } from "hooks/useApiData";
import { useApiState } from "hooks/useApiState";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { useReactiveDefaultDateRange } from "hooks/useReactiveDefaultDateRange";
import { DATE_RANGE_TYPE } from "utils/constants";

const RegionExpensesContainer = () => {
  const dispatch = useDispatch();
  const { organizationId } = useOrganizationInfo();

  const [startDateTimestamp, endDateTimestamp] = useReactiveDefaultDateRange(DATE_RANGE_TYPE.EXPENSES);

  const { isLoading, shouldInvoke } = useApiState(GET_REGION_EXPENSES, {
    startDate: startDateTimestamp,
    endDate: endDateTimestamp,
    organizationId
  });

  useEffect(() => {
    if (shouldInvoke) {
      dispatch(
        getRegionExpenses(organizationId, {
          startDate: startDateTimestamp,
          endDate: endDateTimestamp
        })
      );
    }
  }, [dispatch, endDateTimestamp, organizationId, shouldInvoke, startDateTimestamp]);

  const {
    apiData: { expenses = {} }
  } = useApiData(GET_REGION_EXPENSES);

  return <RegionExpenses isLoading={isLoading} expenses={expenses} />;
};

export default RegionExpensesContainer;
