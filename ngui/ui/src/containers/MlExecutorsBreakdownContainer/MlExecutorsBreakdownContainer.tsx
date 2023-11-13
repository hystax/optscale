import MlExecutorsBreakdown from "components/MlExecutorsBreakdown";
import MlExecutorsService from "services/MlExecutorsService";
import { ML_EXECUTORS_DAILY_BREAKDOWN_BY } from "utils/constants";
import { inDateRange, secondsToMilliseconds } from "utils/datetime";

const MlExecutorsBreakdownContainer = ({ dateRange, breakdownBy = ML_EXECUTORS_DAILY_BREAKDOWN_BY.CPU }) => {
  const getFilteredBreakdown = (breakdown) =>
    Object.fromEntries(
      Object.entries(breakdown).filter(([secondsTimestamp]) => inDateRange(dateRange, secondsToMilliseconds(secondsTimestamp)))
    );

  const { useGetBreakdown } = MlExecutorsService();

  const { breakdown, isLoading } = useGetBreakdown({ breakdownBy });

  return <MlExecutorsBreakdown breakdown={getFilteredBreakdown(breakdown)} breakdownBy={breakdownBy} isLoading={isLoading} />;
};

export default MlExecutorsBreakdownContainer;
