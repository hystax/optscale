import { useEffect } from "react";
import { useDispatch } from "react-redux";
import { getExpensesSummary } from "api";
import { GET_EXPENSES_SUMMARY } from "api/restapi/actionTypes";
import { useApiData } from "hooks/useApiData";
import { useApiState } from "hooks/useApiState";
import { useInScopeOfPageMockup } from "hooks/useInScopeOfPageMockup";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { mapCleanExpensesFilterParamsToApiParams } from "./CleanExpensesService";

const dataMocked = {
  total_cost: 125.22803930100001,
  total_count: 7,
  total_saving: 76.59
};

export const useGet = ({ params = {} } = {}) => {
  const dispatch = useDispatch();
  const inScopeOfPageMockup = useInScopeOfPageMockup();
  const { organizationId } = useOrganizationInfo();
  const { apiData: data } = useApiData(GET_EXPENSES_SUMMARY);

  const { isLoading, shouldInvoke } = useApiState(GET_EXPENSES_SUMMARY, {
    organizationId,
    ...mapCleanExpensesFilterParamsToApiParams(params)
  });

  useEffect(() => {
    if (shouldInvoke && !inScopeOfPageMockup) {
      dispatch(getExpensesSummary(organizationId, mapCleanExpensesFilterParamsToApiParams(params)));
    }
  }, [dispatch, shouldInvoke, params, organizationId, inScopeOfPageMockup]);

  return { isLoading, data: inScopeOfPageMockup ? dataMocked : data };
};

function SummaryService() {
  return { useGet };
}

export default SummaryService;
