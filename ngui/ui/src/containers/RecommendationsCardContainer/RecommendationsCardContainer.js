import React, { useMemo } from "react";
import RecommendationsCard from "components/RecommendationsCard";
import {
  ACTIVE,
  CATEGORY_COST,
  CATEGORY_SECURITY,
  RECOMMENDATION_COLOR
} from "containers/RecommendationsOverviewContainer/recommendations/BaseRecommendation";
import RecommendationsOverviewService from "containers/RecommendationsOverviewContainer/RecommendationsOverviewService";
import { useAllRecommendations } from "hooks/useAllRecommendations";
import ExpensesService from "services/ExpensesService";

const RecommendationsCardContainer = () => {
  const { useGetOrganizationExpenses } = ExpensesService();
  const { isLoading: isGetOrganizationExpensesLoading, data: organizationExpenses } = useGetOrganizationExpenses();
  const { expenses: { this_month_forecast: { total: thisMonthExpensesForecast } = {} } = {} } = organizationExpenses;

  const { useGetOptimizationsOverview } = RecommendationsOverviewService();
  const { isLoading, data } = useGetOptimizationsOverview();

  const { total_saving: possibleMonthlySavings = 0 } = data;

  const allRecommendations = useAllRecommendations();

  const categoriesCounters = useMemo(() => {
    const recommendations = Object.values(allRecommendations).map(
      (RecommendationClass) => new RecommendationClass(ACTIVE, data)
    );

    const { [CATEGORY_COST]: costRecommendationsCount, [CATEGORY_SECURITY]: securityRecommendationsCount } = Object.fromEntries(
      [CATEGORY_COST, CATEGORY_SECURITY].map((category) => [
        category,
        recommendations.reduce((acc, r) => (r.hasCategory(category) ? acc + r.count : acc), 0)
      ])
    );

    const criticalRecommendationsCount = Object.values(allRecommendations)
      .filter(({ color }) => color === RECOMMENDATION_COLOR.ERROR)
      .reduce((acc, r) => acc + r.count, 0);

    return {
      costRecommendationsCount,
      securityRecommendationsCount,
      criticalRecommendationsCount
    };
  }, [allRecommendations, data]);

  const { costRecommendationsCount, securityRecommendationsCount, criticalRecommendationsCount } = categoriesCounters;

  return (
    <RecommendationsCard
      isLoading={isLoading || isGetOrganizationExpensesLoading}
      possibleMonthlySavings={possibleMonthlySavings}
      costRecommendationsCount={costRecommendationsCount}
      securityRecommendationsCount={securityRecommendationsCount}
      criticalRecommendationsCount={criticalRecommendationsCount}
      thisMonthExpensesForecast={thisMonthExpensesForecast}
    />
  );
};

export default RecommendationsCardContainer;
