import React, { useMemo } from "react";
import PropTypes from "prop-types";
import ExpensesDailyBreakdownBy from "components/ExpensesDailyBreakdownBy";
import { useBreakdownBy } from "hooks/useBreakdownBy";
import { mapCleanExpensesFilterParamsToApiParams } from "services/CleanExpensesService";
import DailyExpensesBreakdownByService from "services/DailyExpensesBreakdownByService";
import { DAILY_EXPENSES_BREAKDOWN_BY_PARAMETER_NAME } from "urls";

const ExpensesDailyBreakdownByContainer = ({ cleanExpensesRequestParams }) => {
  const { useGet } = DailyExpensesBreakdownByService();

  const [{ value: breakdownByValue }, onBreakdownByChange] = useBreakdownBy({
    queryParamName: DAILY_EXPENSES_BREAKDOWN_BY_PARAMETER_NAME
  });

  const requestParams = useMemo(
    () => ({ ...mapCleanExpensesFilterParamsToApiParams(cleanExpensesRequestParams), breakdown_by: breakdownByValue }),
    [breakdownByValue, cleanExpensesRequestParams]
  );

  const { isLoading, data: { breakdown = {} } = {} } = useGet(requestParams);

  return (
    <ExpensesDailyBreakdownBy
      isLoading={isLoading}
      breakdown={breakdown}
      breakdownByValue={breakdownByValue}
      onBreakdownByChange={onBreakdownByChange}
    />
  );
};

ExpensesDailyBreakdownByContainer.propTypes = {
  cleanExpensesRequestParams: PropTypes.object.isRequired
};

export default ExpensesDailyBreakdownByContainer;
