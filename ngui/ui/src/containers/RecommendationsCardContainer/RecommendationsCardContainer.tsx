import { useMemo } from "react";
import RecommendationsCard from "components/RecommendationsCard";
import {
  STATUS,
  CATEGORY,
  RECOMMENDATION_COLOR,
} from "containers/RecommendationsOverviewContainer/recommendations/BaseRecommendation";
import { useAllRecommendations } from "hooks/useAllRecommendations";
import ExpensesService from "services/ExpensesService";
import RecommendationsOverviewService from "services/RecommendationsOverviewService";

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
      (RecommendationClass) => new RecommendationClass(STATUS.ACTIVE, data)
    );

    const calculateRecommendationCount = (filterFn) =>
      recommendations.reduce((total, recommendation) => (filterFn(recommendation) ? total + recommendation.count : total), 0);

    const countingCriteria = {
      costRecommendationsCount: (recommendation) => recommendation.hasCategory(CATEGORY.COST),
      securityRecommendationsCount: (recommendation) => recommendation.hasCategory(CATEGORY.SECURITY),
      criticalRecommendationsCount: (recommendation) => recommendation.color === RECOMMENDATION_COLOR.ERROR,
    };

    const counts = Object.fromEntries(
      Object.entries(countingCriteria).map(([key, filterFn]) => [key, calculateRecommendationCount(filterFn)])
    );

    return counts;
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
