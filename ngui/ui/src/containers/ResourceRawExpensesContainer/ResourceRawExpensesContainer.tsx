import { useEffect } from "react";

import { useDispatch } from "react-redux";
import { getRawExpenses } from "api";
import { GET_RAW_EXPENSES } from "api/restapi/actionTypes";
import ResourceRawExpenses from "components/ResourceRawExpenses";
import { useApiData } from "hooks/useApiData";
import { useApiState } from "hooks/useApiState";

const ResourceRawExpensesContainer = ({ resourceId, startDate, endDate, expensesMode }) => {
  const dispatch = useDispatch();

  const { isLoading, shouldInvoke } = useApiState(GET_RAW_EXPENSES, { ...{ startDate, endDate }, resourceId });

  useEffect(() => {
    if (shouldInvoke) {
      dispatch(getRawExpenses(resourceId, { startDate, endDate }));
    }
  }, [dispatch, shouldInvoke, resourceId, startDate, endDate]);

  const {
    apiData: { raw_expenses: expenses = [], total_cost: totalCost = 0 }
  } = useApiData(GET_RAW_EXPENSES);

  return (
    <ResourceRawExpenses
      startDate={startDate}
      endDate={endDate}
      shownExpenses={totalCost}
      expenses={expenses}
      isLoading={isLoading}
      expensesMode={expensesMode}
    />
  );
};

export default ResourceRawExpensesContainer;
