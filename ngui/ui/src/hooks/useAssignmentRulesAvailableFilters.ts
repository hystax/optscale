import { useMemo } from "react";
import AvailableFiltersService from "services/AvailableFiltersService";
import { getXDaysAgoRange } from "utils/datetime";

export const useAssignmentRulesAvailableFilters = () => {
  const { useGet: useGetAvailableFilters } = AvailableFiltersService();
  const getAvailableFiltersParams = useMemo(() => {
    const range = getXDaysAgoRange(true, 29);

    return {
      startDate: range.start,
      endDate: range.end
    };
  }, []);

  const { isLoading, filters: availableFilters = {} } = useGetAvailableFilters(getAvailableFiltersParams);

  const resourceTypes = availableFilters?.resource_type ?? [];
  const regions = availableFilters?.region ?? [];

  return {
    isLoading,
    resourceTypes,
    regions
  };
};
