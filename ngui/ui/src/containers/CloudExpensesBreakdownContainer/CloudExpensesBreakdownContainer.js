import React, { useEffect } from "react";
import PropTypes from "prop-types";
import { useDispatch } from "react-redux";
import { getCloudsExpenses } from "api";
import { GET_CLOUDS_EXPENSES } from "api/restapi/actionTypes";
import ExpensesBreakdown from "components/ExpensesBreakdown";
import { useApiState } from "hooks/useApiState";
import { useExpensesBreakdownRequestParams } from "hooks/useExpensesBreakdownRequestParams";
import { useExpensesData } from "hooks/useExpensesData";

const CloudExpensesBreakdownContainer = ({ type, entityId: cloudAccountId }) => {
  const dispatch = useDispatch();

  const {
    filterBy,
    startDateTimestamp,
    endDateTimestamp,
    breakdown,
    name,
    total,
    previousTotal,
    filteredBreakdown,
    dataSourceType
  } = useExpensesData(GET_CLOUDS_EXPENSES);

  const [requestParams, applyFilter, updateFilter] = useExpensesBreakdownRequestParams({
    filterBy,
    startDateTimestamp,
    endDateTimestamp
  });

  const { isLoading, shouldInvoke } = useApiState(GET_CLOUDS_EXPENSES, { ...requestParams, cloudAccountId });

  useEffect(() => {
    if (shouldInvoke) {
      dispatch(getCloudsExpenses(cloudAccountId, requestParams));
    }
  }, [cloudAccountId, dispatch, requestParams, shouldInvoke]);

  return (
    <ExpensesBreakdown
      entityId={cloudAccountId}
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
      dataSourceType={dataSourceType}
    />
  );
};

CloudExpensesBreakdownContainer.propTypes = {
  type: PropTypes.string.isRequired,
  entityId: PropTypes.string
};

export default CloudExpensesBreakdownContainer;
