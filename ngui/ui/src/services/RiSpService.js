import { useEffect } from "react";
import { useDispatch } from "react-redux";
import { getRiSpUsageBreakdown, getRiSpExpensesBreakdown } from "api";
import { GET_RI_SP_USAGE_BREAKDOWN, GET_RI_SP_EXPENSES_BREAKDOWN } from "api/restapi/actionTypes";
import { useApiData } from "hooks/useApiData";
import { useApiState } from "hooks/useApiState";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";

const useGetUsageBreakdown = (startDate, endDate, dataSourceIds) => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();

  const { apiData } = useApiData(GET_RI_SP_USAGE_BREAKDOWN, {});

  const { isLoading, shouldInvoke } = useApiState(GET_RI_SP_USAGE_BREAKDOWN, {
    organizationId,
    startDate,
    endDate,
    dataSourceIds
  });

  useEffect(() => {
    if (shouldInvoke) {
      dispatch(getRiSpUsageBreakdown(organizationId, { startDate, endDate, dataSourceIds }));
    }
  }, [shouldInvoke, dispatch, organizationId, startDate, endDate, dataSourceIds]);

  return { isLoading, breakdown: apiData };
};

const useGetExpensesBreakdown = (startDate, endDate, dataSourceIds) => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();

  const { apiData } = useApiData(GET_RI_SP_EXPENSES_BREAKDOWN, {});

  const { isLoading, shouldInvoke } = useApiState(GET_RI_SP_EXPENSES_BREAKDOWN, {
    organizationId,
    startDate,
    endDate,
    dataSourceIds
  });

  useEffect(() => {
    if (shouldInvoke) {
      dispatch(getRiSpExpensesBreakdown(organizationId, { startDate, endDate, dataSourceIds }));
    }
  }, [shouldInvoke, dispatch, organizationId, startDate, endDate, dataSourceIds]);

  return { isLoading, breakdown: apiData };
};

function RiSpService() {
  return {
    useGetUsageBreakdown,
    useGetExpensesBreakdown
  };
}

export default RiSpService;
