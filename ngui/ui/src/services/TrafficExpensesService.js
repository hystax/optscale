import { useEffect } from "react";
import { useDispatch } from "react-redux";
import { getTrafficExpenses } from "api";
import { GET_TRAFFIC_EXPENSES } from "api/restapi/actionTypes";
import { useApiData } from "hooks/useApiData";
import { useApiState } from "hooks/useApiState";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";

const useGetTrafficExpenses = ({ startDate, endDate, resourceId }) => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();

  const { isLoading, shouldInvoke } = useApiState(GET_TRAFFIC_EXPENSES, {
    startDate,
    endDate,
    resourceId,
    organizationId
  });

  useEffect(() => {
    if (shouldInvoke) {
      dispatch(
        getTrafficExpenses(organizationId, {
          startDate,
          endDate,
          resourceId
        })
      );
    }
  }, [dispatch, shouldInvoke, organizationId, startDate, endDate, resourceId]);

  const {
    apiData: { expenses: trafficExpenses = [] }
  } = useApiData(GET_TRAFFIC_EXPENSES);

  return { trafficExpenses, isLoading };
};

function TrafficExpensesService() {
  return { useGetTrafficExpenses };
}

export default TrafficExpensesService;
