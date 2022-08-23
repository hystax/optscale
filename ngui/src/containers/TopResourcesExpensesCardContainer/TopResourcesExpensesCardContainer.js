import React, { useMemo } from "react";
import TopResourcesExpensesCard from "components/TopResourcesExpensesCard";
import CleanExpensesService from "services/CleanExpensesService";
import { getLast30DaysRange } from "utils/datetime";

const TopResourcesExpensesCardContainer = () => {
  const { useGet } = CleanExpensesService();

  const params = useMemo(() => {
    const { startDate, endDate } = getLast30DaysRange();

    return {
      limit: 5,
      startDate,
      endDate
    };
  }, []);

  const {
    isLoading,
    data: { clean_expenses: cleanExpenses = [] }
  } = useGet({
    params
  });

  return <TopResourcesExpensesCard isLoading={isLoading} cleanExpenses={cleanExpenses} />;
};

export default TopResourcesExpensesCardContainer;
