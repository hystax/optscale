import React from "react";
import RecommendationsCard from "components/RecommendationsCard";
import RecommendationService from "services/RecommendationService";

const RecommendationsCardContainer = () => {
  const { useGetRelevantOptimizations } = RecommendationService();

  const { isLoading, data } = useGetRelevantOptimizations();

  const {
    optimizations: {
      categoriesSizes: { cost: costRecommendationsCount = 0, security: securityRecommendationsCount = 0 } = {},
      total_saving: possibleMonthlySavings = 0
    } = {}
  } = data;

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
