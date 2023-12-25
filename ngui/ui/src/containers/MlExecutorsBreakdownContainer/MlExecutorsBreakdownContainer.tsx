import { useMemo } from "react";
import MlExecutorsBreakdownLineChart from "components/MlExecutorsBreakdownLineChart";
import MlExecutorsService from "services/MlExecutorsService";
import { inDateRange, secondsToMilliseconds } from "utils/datetime";

const MlExecutorsBreakdownContainer = ({ dateRange }) => {
  const { useGetBreakdown } = MlExecutorsService();

  const { breakdown, isLoading } = useGetBreakdown();

  const filteredBreakdown = useMemo(
    () =>
      Object.fromEntries(
        Object.entries(breakdown).filter(([secondsTimestamp]) =>
          inDateRange(dateRange, secondsToMilliseconds(secondsTimestamp))
        )
      ),
    [breakdown, dateRange]
  );

  return <MlExecutorsBreakdownLineChart breakdown={filteredBreakdown} isLoading={isLoading} />;
};

export default MlExecutorsBreakdownContainer;
