import { useEffect } from "react";
import { useDispatch } from "react-redux";
import { getDailyExpensesBreakdown } from "api";
import { GET_EXPENSES_DAILY_BREAKDOWN } from "api/restapi/actionTypes";
import { useApiData } from "hooks/useApiData";
import { useApiState } from "hooks/useApiState";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";

export const useGet = (params) => {
  const dispatch = useDispatch();
  const { organizationId } = useOrganizationInfo();

  const { isLoading, shouldInvoke } = useApiState(GET_EXPENSES_DAILY_BREAKDOWN, { organizationId, ...params });

  useEffect(() => {
    if (shouldInvoke) {
      dispatch(getDailyExpensesBreakdown(organizationId, params));
    }
  }, [dispatch, organizationId, shouldInvoke, params]);

  const { apiData } = useApiData(GET_EXPENSES_DAILY_BREAKDOWN, {});

  return { isLoading, data: apiData };
};

function DailyExpensesBreakdownByService() {
  return { useGet };
}

export default DailyExpensesBreakdownByService;
