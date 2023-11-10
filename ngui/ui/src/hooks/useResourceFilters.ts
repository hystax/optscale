import { GET_CURRENT_EMPLOYEE } from "api/restapi/actionTypes";
import Filters from "components/Filters";
import { RESOURCE_FILTERS } from "components/Filters/constants";
import { useApiData } from "./useApiData";

export const useResourceFilters = (filterValues, appliedFilters) => {
  const { apiData: { currentEmployee: { id: currentEmployeeId } = {} } = {} } = useApiData(GET_CURRENT_EMPLOYEE);

  const scopeInfo = { currentEmployeeId };

  return new Filters({
    filters: RESOURCE_FILTERS,
    filterValues,
    appliedFilters,
    scopeInfo
  });
};
