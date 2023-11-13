import { useEffect } from "react";
import { useDispatch } from "react-redux";
import { getTrafficExpenses } from "api";
import { GET_TRAFFIC_EXPENSES } from "api/restapi/actionTypes";
import TrafficExpenses from "components/TrafficExpenses";
import { useApiData } from "hooks/useApiData";
import { useApiState } from "hooks/useApiState";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { useReactiveDefaultDateRange } from "hooks/useReactiveDefaultDateRange";
import { DATE_RANGE_TYPE } from "utils/constants";

const TrafficExpensesContainer = () => {
  const dispatch = useDispatch();
  const { organizationId } = useOrganizationInfo();

  const [startDateTimestamp, endDateTimestamp] = useReactiveDefaultDateRange(DATE_RANGE_TYPE.EXPENSES);

  const { isDataReady, shouldInvoke } = useApiState(GET_TRAFFIC_EXPENSES, {
    startDate: startDateTimestamp,
    endDate: endDateTimestamp,
    organizationId
  });

  useEffect(() => {
    if (shouldInvoke) {
      dispatch(
        getTrafficExpenses(organizationId, {
          startDate: startDateTimestamp,
          endDate: endDateTimestamp
        })
      );
    }
  }, [dispatch, endDateTimestamp, organizationId, shouldInvoke, startDateTimestamp]);

  const {
    apiData: { expenses = {} }
  } = useApiData(GET_TRAFFIC_EXPENSES);

  return <TrafficExpenses isLoading={!isDataReady} expenses={expenses} />;
};

export default TrafficExpensesContainer;
