import RiSpCoverage from "components/RiSpCoverage";
import { useRiSpBreakdowns } from "hooks/useRiSpBreakdowns";

type RiSpCoverageContainerProps = {
  startDate: number;
  endDate: number;
  dataSourceIds: string[];
};

const RiSpCoverageContainer = ({ startDate, endDate, dataSourceIds }: RiSpCoverageContainerProps) => {
  const { isLoading, expensesBreakdown, usageBreakdown } = useRiSpBreakdowns({
    startDate,
    endDate,
    dataSourceIds
  });

  return (
    <RiSpCoverage
      usageBreakdown={usageBreakdown}
      expensesBreakdown={expensesBreakdown}
      isLoadingProps={{
        isGetUsageBreakdownLoading: isLoading,
        isGetExpensesBreakdownLoading: isLoading
      }}
    />
  );
};
export default RiSpCoverageContainer;
