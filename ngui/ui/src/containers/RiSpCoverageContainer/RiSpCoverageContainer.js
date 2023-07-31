import React from "react";
import RiSpCoverage from "components/RiSpCoverage";
import RiSpService from "services/RiSpService";

const RiSpCoverageContainer = ({ startDate, endDate, dataSourceIds }) => {
  const { useGetUsageBreakdown, useGetExpensesBreakdown } = RiSpService();

  const { isLoading: isGetUsageBreakdownLoading, breakdown: usageBreakdown } = useGetUsageBreakdown(
    startDate,
    endDate,
    dataSourceIds
  );
  const { isLoading: isGetExpensesBreakdownLoading, breakdown: expensesBreakdown } = useGetExpensesBreakdown(
    startDate,
    endDate,
    dataSourceIds
  );

  return (
    <RiSpCoverage
      usageBreakdown={usageBreakdown}
      expensesBreakdown={expensesBreakdown}
      isLoadingProps={{ isGetUsageBreakdownLoading, isGetExpensesBreakdownLoading }}
    />
  );
};
export default RiSpCoverageContainer;
