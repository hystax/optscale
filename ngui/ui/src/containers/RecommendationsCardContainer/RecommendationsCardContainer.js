import React, { useMemo } from "react";
import RecommendationsCard from "components/RecommendationsCard";
import { ALL_RECOMMENDATIONS } from "containers/RecommendationsOverviewContainer/recommendations/allRecommendations";
import {
  ACTIVE,
  CATEGORY_COST,
  CATEGORY_SECURITY
} from "containers/RecommendationsOverviewContainer/recommendations/BaseRecommendation";
import RecommendationsOverviewService from "containers/RecommendationsOverviewContainer/RecommendationsOverviewService";

const RecommendationsCardContainer = () => {
  const { useGetOptimizationsOverview } = RecommendationsOverviewService();
  const { isLoading, data } = useGetOptimizationsOverview();

  const { total_saving: possibleMonthlySavings = 0 } = data;

  const categoriesCounters = useMemo(() => {
    const allRecommendations = Object.values(ALL_RECOMMENDATIONS).map(
      (RecommendationClass) => new RecommendationClass(ACTIVE, data)
    );
    return Object.fromEntries(
      [CATEGORY_COST, CATEGORY_SECURITY].map((category) => [
        category,
        allRecommendations.reduce((acc, r) => (r.hasCategory(category) ? acc + r.count : acc), 0)
      ])
    );
  }, [data]);
  const { [CATEGORY_COST]: costRecommendationsCount, [CATEGORY_SECURITY]: securityRecommendationsCount } = categoriesCounters;

  return (
    <RecommendationsCard
      isLoading={isLoading}
      possibleMonthlySavings={possibleMonthlySavings}
      costRecommendationsCount={costRecommendationsCount}
      securityRecommendationsCount={securityRecommendationsCount}
    />
  );
};

export default RecommendationsCardContainer;
