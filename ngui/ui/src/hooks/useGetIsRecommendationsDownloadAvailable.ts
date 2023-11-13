import { FREE_ACCOUNT_30_DAYS_EXPENSES_THRESHOLD } from "utils/constants";
import { useGetLast30DaysOrganizationExpenses } from "./useGetLast30DaysOrganizationExpenses";
import { useIsPaidOrganization } from "./useIsPaidOrganization";

export const useGetIsRecommendationsDownloadAvailable = (url) => {
  const isPaidOrganization = useIsPaidOrganization();

  const { isLoading, isError, last30DaysOrganizationExpenses } = useGetLast30DaysOrganizationExpenses(url);

  return {
    isLoading,
    isDownloadAvailable:
      !isError && (isPaidOrganization || last30DaysOrganizationExpenses <= FREE_ACCOUNT_30_DAYS_EXPENSES_THRESHOLD)
  };
};
