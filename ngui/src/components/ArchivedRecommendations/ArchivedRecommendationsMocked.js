import React from "react";
import ArchivedRecommendations from "components/ArchivedRecommendations/index";
import { addDaysToTimestamp, getLastWeekRange } from "utils/datetime";

const ArchivedRecommendationsMocked = () => {
  const { lastWeekStart: firstDateRangePoint, lastWeekEnd: lastDateRangePoint } = getLastWeekRange(true);

  const archivedRecommendationsBreakdown = [
    {
      count: 2,
      module: "abandoned_instances",
      archived_at: addDaysToTimestamp(firstDateRangePoint, 1),
      reason: "recommendation_applied"
    },
    {
      count: 1,
      module: "abandoned_instances",
      archived_at: addDaysToTimestamp(firstDateRangePoint, 2),
      reason: "recommendation_irrelevant"
    },
    {
      count: 1,
      module: "abandoned_instances",
      archived_at: addDaysToTimestamp(firstDateRangePoint, 4),
      reason: "recommendation_irrelevant"
    },
    {
      count: 1,
      module: "abandoned_instances",
      archived_at: addDaysToTimestamp(firstDateRangePoint, 5),
      reason: "recommendation_irrelevant"
    }
  ];

  const archivedRecommendationsChartBreakdown = {
    [addDaysToTimestamp(firstDateRangePoint, 1)]: { abandoned_instances: { recommendation_irrelevant: 2 } },
    [addDaysToTimestamp(firstDateRangePoint, 2)]: { abandoned_instances: { recommendation_applied: 1 } },
    [addDaysToTimestamp(firstDateRangePoint, 4)]: { abandoned_instances: { recommendation_irrelevant: 1 } },
    [addDaysToTimestamp(firstDateRangePoint, 5)]: { abandoned_instances: { recommendation_irrelevant: 1 } }
  };

  return (
    <ArchivedRecommendations
      onTimeRangeChange={() => console.log("handleTimeRangeChange")}
      onBarChartSelect={() => console.log("handleBarChartSelect")}
      dateRange={{ endDate: lastDateRangePoint, startDate: firstDateRangePoint }}
      archivedRecommendationsChartBreakdown={archivedRecommendationsChartBreakdown}
      archivedRecommendationsBreakdown={archivedRecommendationsBreakdown}
      isChartLoading={false}
      isLoading={false}
    />
  );
};

export default ArchivedRecommendationsMocked;
