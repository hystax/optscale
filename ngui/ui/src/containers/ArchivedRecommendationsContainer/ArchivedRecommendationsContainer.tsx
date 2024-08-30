import { useEffect, useState } from "react";
import ArchivedRecommendations from "components/ArchivedRecommendations";
import { useIsNebiusConnectionEnabled } from "hooks/useIsNebiusConnectionEnabled";
import { NEBIUS_RECOMMENDATION_TYPES } from "hooks/useOptscaleRecommendations";
import { useReactiveDefaultDateRange } from "hooks/useReactiveDefaultDateRange";
import ArchivedRecommendationService from "services/ArchivedRecommendationService";
import { DATE_RANGE_TYPE } from "utils/constants";
import { updateQueryParams } from "utils/network";

const ArchivedRecommendationsContainer = () => {
  const isNebiusConnectionEnabled = useIsNebiusConnectionEnabled();

  const { useGetArchivedOptimizationsBreakdown, useGetArchivedOptimizationsCount } = ArchivedRecommendationService();

  const [startDateTimestamp, endDateTimestamp] = useReactiveDefaultDateRange(DATE_RANGE_TYPE.ARCHIVED_RECOMMENDATIONS);

  const [dateRange, setDateRange] = useState({
    startDate: startDateTimestamp,
    endDate: endDateTimestamp
  });

  const [breakdownDateRange, setBreakdownDateRange] = useState(dateRange);

  useEffect(() => {
    updateQueryParams(dateRange);
  }, [dateRange]);

  const { isLoading: isChartLoading, data: { breakdown: archivedRecommendationsChartBreakdown = {} } = {} } =
    useGetArchivedOptimizationsCount(dateRange);

  const {
    isLoading,
    data: { breakdown: archivedRecommendationsBreakdown = [] }
  } = useGetArchivedOptimizationsBreakdown(breakdownDateRange);

  const onTimeRangeChange = ({ startDate, endDate }) => {
    setDateRange({
      startDate,
      endDate
    });
    setBreakdownDateRange({
      startDate,
      endDate
    });
  };

  const filteredArchivedRecommendationsChartBreakdown = Object.fromEntries(
    Object.entries(archivedRecommendationsChartBreakdown).map(([date, breakdown]) => {
      const filteredBreakdown = Object.fromEntries(
        Object.entries(breakdown).filter(([key]) => {
          if (NEBIUS_RECOMMENDATION_TYPES.includes(key)) {
            return isNebiusConnectionEnabled;
          }
          return true;
        })
      );

      return [date, filteredBreakdown];
    })
  );

  const filteredArchivedRecommendationsBreakdown = archivedRecommendationsBreakdown.filter(({ module }) => {
    if (NEBIUS_RECOMMENDATION_TYPES.includes(module)) {
      return isNebiusConnectionEnabled;
    }
    return true;
  });

  return (
    <ArchivedRecommendations
      onTimeRangeChange={onTimeRangeChange}
      onBarChartSelect={(range) => setBreakdownDateRange(range || dateRange)}
      dateRange={dateRange}
      archivedRecommendationsChartBreakdown={filteredArchivedRecommendationsChartBreakdown}
      archivedRecommendationsBreakdown={filteredArchivedRecommendationsBreakdown}
      isChartLoading={isChartLoading}
      isLoading={isLoading}
    />
  );
};

export default ArchivedRecommendationsContainer;
