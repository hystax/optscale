import { useEffect } from "react";
import { useDispatch } from "react-redux";
import { getEmployeesExpenses } from "api";
import { GET_EMPLOYEES_EXPENSES } from "api/restapi/actionTypes";
import ExpensesBreakdown from "components/ExpensesBreakdown";
import { useApiState } from "hooks/useApiState";
import { useExpensesBreakdownRequestParams } from "hooks/useExpensesBreakdownRequestParams";
import { useExpensesData } from "hooks/useExpensesData";

const EmployeeExpensesBreakdownContainer = ({ type, entityId: employeeId }) => {
  const dispatch = useDispatch();

  const { filterBy, startDateTimestamp, endDateTimestamp, breakdown, name, total, previousTotal, filteredBreakdown } =
    useExpensesData(GET_EMPLOYEES_EXPENSES);

  const [requestParams, applyFilter, updateFilter] = useExpensesBreakdownRequestParams({
    filterBy,
    startDateTimestamp,
    endDateTimestamp
  });

  const { isLoading, shouldInvoke } = useApiState(GET_EMPLOYEES_EXPENSES, { ...requestParams, employeeId });

  useEffect(() => {
    if (shouldInvoke) {
      dispatch(getEmployeesExpenses(employeeId, requestParams));
    }
  }, [employeeId, dispatch, requestParams, shouldInvoke]);

  return (
    <ExpensesBreakdown
      entityId={employeeId}
      filterBy={filterBy}
      type={type}
      breakdown={breakdown}
      total={total}
      previousTotal={previousTotal}
      filteredBreakdown={filteredBreakdown}
      startDateTimestamp={startDateTimestamp}
      endDateTimestamp={endDateTimestamp}
      isLoading={isLoading}
      onApply={applyFilter}
      updateFilter={updateFilter}
      name={name}
    />
  );
};

export default EmployeeExpensesBreakdownContainer;
