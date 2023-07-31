import { useMemo } from "react";
import SummaryService from "services/SummaryService";
import { getLast30DaysRange } from "utils/datetime";

export const useGetLast30DaysOrganizationExpenses = (url) => {
  const { startDate, endDate } = getLast30DaysRange();

  const { useGet } = SummaryService();

  const parameters = useMemo(
    () => ({
      params: {
        startDate,
        endDate
      },
      url
    }),
    [endDate, startDate, url]
  );

  const {
    isLoading,
    isError,
    data: { total_cost: totalExpenses }
  } = useGet(parameters);

  return {
    isLoading,
    isError,
    last30DaysOrganizationExpenses: totalExpenses
  };
};
