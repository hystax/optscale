import { FILTER_TYPE } from "components/FilterComponents/constants";
import { FILTER_CONFIGS } from "components/Resources/filterConfigs";
import { RESOURCES, RESOURCES_BREAKDOWN_BY_QUERY_PARAMETER_NAME } from "urls";
import { isEmptyArray } from "utils/arrays";
import {
  CLEAN_EXPENSES_BREAKDOWN_TYPES,
  END_DATE_FILTER,
  EXPENSE_ANOMALY,
  EXPIRING_BUDGET_POLICY,
  QUOTA_POLICY,
  RECURRING_BUDGET_POLICY,
  RESOURCE_COUNT_ANOMALY,
  START_DATE_FILTER,
  TAGGING_POLICY,
} from "utils/constants";
import { stringifySearchParams } from "utils/network";
import { getFilterValues } from "./getFilterValues";

const constraintTypeToResourcesBreakdownMap = {
  [EXPENSE_ANOMALY]: CLEAN_EXPENSES_BREAKDOWN_TYPES.EXPENSES,
  [RESOURCE_COUNT_ANOMALY]: CLEAN_EXPENSES_BREAKDOWN_TYPES.RESOURCE_COUNT,
  [QUOTA_POLICY]: CLEAN_EXPENSES_BREAKDOWN_TYPES.RESOURCE_COUNT,
  [RECURRING_BUDGET_POLICY]: CLEAN_EXPENSES_BREAKDOWN_TYPES.EXPENSES,
  [EXPIRING_BUDGET_POLICY]: CLEAN_EXPENSES_BREAKDOWN_TYPES.EXPENSES,
  [TAGGING_POLICY]: CLEAN_EXPENSES_BREAKDOWN_TYPES.EXPENSES,
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
  const filterValues = getFilterValues(constraint);

  const filterKeyValuePairs = Object.values(FILTER_CONFIGS).flatMap((config) => {
    if (config.type === FILTER_TYPE.SELECTION) {
      const appliedFilters = filterValues[config.apiName] ?? [];

      if (isEmptyArray(appliedFilters)) {
        return [];
      }

      return [[config.id, appliedFilters.map((appliedFilter) => config.transformers.getValue(appliedFilter))]];
    }

    if (config.type === FILTER_TYPE.RANGE) {
      const from = filterValues[config.fromApiName];
      const to = filterValues[config.toApiName];

      if (!from && !to) {
        return [];
      }

      return [
        [config.fromName, from],
        [config.toName, to],
      ];
    }
    return [];
  });

  return stringifySearchParams(Object.fromEntries(filterKeyValuePairs));
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
