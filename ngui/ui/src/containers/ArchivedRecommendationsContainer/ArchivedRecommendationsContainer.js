import React, { useEffect, useState } from "react";
import ArchivedRecommendations from "components/ArchivedRecommendations";
import { useReactiveDefaultDateRange } from "hooks/useReactiveDefaultDateRange";
import ArchivedRecommendationService from "services/ArchivedRecommendationService";
import { DATE_RANGE_TYPE } from "utils/constants";
import { updateQueryParams } from "utils/network";

const ArchivedRecommendationsContainer = () => {
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

  return (
    <ArchivedRecommendations
      onTimeRangeChange={onTimeRangeChange}
      onBarChartSelect={(range) => setBreakdownDateRange(range || dateRange)}
      dateRange={dateRange}
      archivedRecommendationsChartBreakdown={archivedRecommendationsChartBreakdown}
      archivedRecommendationsBreakdown={archivedRecommendationsBreakdown}
      isChartLoading={isChartLoading}
      isLoading={isLoading}
    />
  );
};

export default ArchivedRecommendationsContainer;
