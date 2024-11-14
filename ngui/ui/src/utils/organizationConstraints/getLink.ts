import Filters from "components/Filters";
import { RESOURCE_FILTERS } from "components/Filters/constants";
import { RESOURCES, RESOURCES_BREAKDOWN_BY_QUERY_PARAMETER_NAME } from "urls";
import {
  CLEAN_EXPENSES_BREAKDOWN_TYPES,
  END_DATE_FILTER,
  EXPENSE_ANOMALY,
  EXPIRING_BUDGET_POLICY,
  QUOTA_POLICY,
  RECURRING_BUDGET_POLICY,
  RESOURCE_COUNT_ANOMALY,
  START_DATE_FILTER,
  TAGGING_POLICY
} from "utils/constants";

const constraintTypeToResourcesBreakdownMap = {
  [EXPENSE_ANOMALY]: CLEAN_EXPENSES_BREAKDOWN_TYPES.EXPENSES,
  [RESOURCE_COUNT_ANOMALY]: CLEAN_EXPENSES_BREAKDOWN_TYPES.RESOURCE_COUNT,
  [QUOTA_POLICY]: CLEAN_EXPENSES_BREAKDOWN_TYPES.RESOURCE_COUNT,
  [RECURRING_BUDGET_POLICY]: CLEAN_EXPENSES_BREAKDOWN_TYPES.EXPENSES,
  [EXPIRING_BUDGET_POLICY]: CLEAN_EXPENSES_BREAKDOWN_TYPES.EXPENSES,
  [TAGGING_POLICY]: CLEAN_EXPENSES_BREAKDOWN_TYPES.EXPENSES
} as const;

const getResourcesBreakdown = (
  type:
    | typeof EXPENSE_ANOMALY
    | typeof RESOURCE_COUNT_ANOMALY
    | typeof QUOTA_POLICY
    | typeof RECURRING_BUDGET_POLICY
    | typeof EXPIRING_BUDGET_POLICY
    | typeof TAGGING_POLICY
) => constraintTypeToResourcesBreakdownMap[type];

const getFiltersParams = (constraint) => {
  // Implicit filters might be returned in conditions, since they are excluded in available filters, e.g. tagging policies
  const allFilters = {
    ...constraint.filters,
    ...(constraint.type === TAGGING_POLICY
      ? Object.entries(constraint.definition?.conditions ?? {}).reduce(
          (result, [key, value]) => ({ ...result, [key]: [value] }),
          {}
        )
      : {})
  };

  const filtersInstance = new Filters({
    filters: RESOURCE_FILTERS,
    filterValues: allFilters
  });

  return filtersInstance.toQueryParametersString();
};

const getBreakdownParameter = (constraint) =>
  `${RESOURCES_BREAKDOWN_BY_QUERY_PARAMETER_NAME}=${getResourcesBreakdown(constraint.type)}`;

const getQueryParams = (constraint, dateRange) => {
  const filtersQueryParams = getFiltersParams(constraint);
  const dateRangeQueryParams = [`${START_DATE_FILTER}=${dateRange.startDate}`, `${END_DATE_FILTER}=${dateRange.endDate}`].join(
    "&"
  );
  const breakdownByQueryParam = getBreakdownParameter(constraint);
  const queryParams = [filtersQueryParams, dateRangeQueryParams, breakdownByQueryParam].join("&");

  return queryParams;
};

export const getLink = ({ dateRange, constraint }) => {
  const queryParams = getQueryParams(constraint, dateRange);

  return `${RESOURCES}?${queryParams}`;
};
