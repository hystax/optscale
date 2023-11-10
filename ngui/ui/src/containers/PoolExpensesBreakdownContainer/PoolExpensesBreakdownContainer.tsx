import { useEffect } from "react";
import { useDispatch } from "react-redux";
import { getPoolExpenses } from "api";
import { GET_POOLS_EXPENSES } from "api/restapi/actionTypes";
import CostExplorer from "components/CostExplorer";
import ExpensesBreakdown from "components/ExpensesBreakdown";
import { useApiState } from "hooks/useApiState";
import { useExpensesBreakdownRequestParams } from "hooks/useExpensesBreakdownRequestParams";
import { useExpensesData } from "hooks/useExpensesData";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { COST_EXPLORER } from "utils/constants";

const PoolExpensesBreakdownContainer = ({ type, entityId: poolId }) => {
  const dispatch = useDispatch();

  const { organizationPoolId } = useOrganizationInfo();

  const { filterBy, startDateTimestamp, endDateTimestamp, breakdown, name, total, previousTotal, filteredBreakdown } =
    useExpensesData(GET_POOLS_EXPENSES);

  const [requestParams, applyFilter, updateFilter] = useExpensesBreakdownRequestParams({
    filterBy,
    startDateTimestamp,
    endDateTimestamp
  });

  const getIdValue = () => poolId || organizationPoolId;

  const idValue = getIdValue();

  const { isLoading, shouldInvoke } = useApiState(GET_POOLS_EXPENSES, { ...requestParams, poolId: idValue });

  useEffect(() => {
    if (shouldInvoke) {
      dispatch(getPoolExpenses(idValue, requestParams));
    }
  }, [dispatch, idValue, requestParams, shouldInvoke]);

  const render = () => {
    if (type === COST_EXPLORER) {
      return filterBy ? (
        <ExpensesBreakdown
          entityId={poolId}
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
      ) : (
        <CostExplorer
          total={total}
          previousTotal={previousTotal}
          breakdown={breakdown}
          organizationName={name}
          isLoading={isLoading}
          onApply={applyFilter}
          startDateTimestamp={startDateTimestamp}
          endDateTimestamp={endDateTimestamp}
        />
      );
    }
    return (
      <ExpensesBreakdown
        entityId={poolId}
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

  return render();
};

export default PoolExpensesBreakdownContainer;
