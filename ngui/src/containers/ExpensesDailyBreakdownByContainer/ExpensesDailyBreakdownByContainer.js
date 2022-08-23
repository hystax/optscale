import React, { useMemo } from "react";
import PropTypes from "prop-types";
import ExpensesDailyBreakdownBy from "components/ExpensesDailyBreakdownBy";
import { useBreakdownBy } from "hooks/useBreakdownBy";
import { mapCleanExpensesFilterParamsToApiParams } from "services/CleanExpensesService";
import DailyExpensesBreakdownByService from "services/DailyExpensesBreakdownByService";

const DAILY_EXPENSES_BREAKDOWN_QUERY_PARAM_NAME = "dailyExpensesBreakdownBy";

const ExpensesDailyBreakdownByContainer = ({ cleanExpensesRequestParams }) => {
  const { useGet } = DailyExpensesBreakdownByService();

  const [breakdownBy, onBreakdownByChange] = useBreakdownBy({ queryParamName: DAILY_EXPENSES_BREAKDOWN_QUERY_PARAM_NAME });

  const requestParams = useMemo(
    () => ({ ...mapCleanExpensesFilterParamsToApiParams(cleanExpensesRequestParams), breakdown_by: breakdownBy }),
    [breakdownBy, cleanExpensesRequestParams]
  );

  const { isLoading, data: { breakdown = {} } = {} } = useGet(requestParams);

  return (
    <ExpensesDailyBreakdownBy
      isLoading={isLoading}
      breakdown={breakdown}
      breakdownBy={breakdownBy}
      onBreakdownByChange={onBreakdownByChange}
    />
  );
};

ExpensesDailyBreakdownByContainer.propTypes = {
  cleanExpensesRequestParams: PropTypes.object.isRequired
};

export default ExpensesDailyBreakdownByContainer;
