import React, { useEffect, useMemo } from "react";
import { useNavigate } from "react-router-dom";
import { areSearchParamsEqual } from "api/utils";
import { RESOURCE_FILTERS_NAMES } from "components/Filters/constants";
import Resources from "components/Resources";
import { useOrganizationPerspectives } from "hooks/useOrganizationPerspectives";
import { useReactiveDefaultDateRange } from "hooks/useReactiveDefaultDateRange";
import { useReactiveSearchParams } from "hooks/useReactiveSearchParams";
import AvailableFiltersService from "services/AvailableFiltersService";
import {
  DAILY_EXPENSES_BREAKDOWN_BY_PARAMETER_NAME,
  DAILY_RESOURCE_COUNT_BREAKDOWN_BY_PARAMETER_NAME,
  getResourcesExpensesUrl,
  GROUP_BY_PARAM_NAME,
  GROUP_TYPE_PARAM_NAME,
  RESOURCES_BREAKDOWN_BY_QUERY_PARAMETER_NAME,
  RESOURCES_SELECTED_PERSPECTIVE_PARAMETER_NAME
} from "urls";
import { getLength } from "utils/arrays";
import {
  DATE_RANGE_TYPE,
  EXPENSES_LIMIT_FILTER_DEFAULT_VALUE,
  BREAKDOWN_LINEAR_SELECTOR_ITEMS,
  CLEAN_EXPENSES_BREAKDOWN_TYPES
} from "utils/constants";
import { getQueryParams, removeQueryParam, updateQueryParams } from "utils/network";

const ResourcesContainer = () => {
  const navigate = useNavigate();

  const { [RESOURCES_SELECTED_PERSPECTIVE_PARAMETER_NAME]: perspectiveNameSearchParameter } = useReactiveSearchParams(
    useMemo(() => [RESOURCES_SELECTED_PERSPECTIVE_PARAMETER_NAME], [])
  );

  const { validPerspectives } = useOrganizationPerspectives();

  const filtersQueryParams = useReactiveSearchParams(RESOURCE_FILTERS_NAMES);

  const [startDateTimestamp, endDateTimestamp] = useReactiveDefaultDateRange(DATE_RANGE_TYPE.RESOURCES);

  const { [RESOURCES_BREAKDOWN_BY_QUERY_PARAMETER_NAME]: breakdownQueryParameter } = useReactiveSearchParams(
    useMemo(() => [RESOURCES_BREAKDOWN_BY_QUERY_PARAMETER_NAME], [])
  );

  const groupByParameters = useReactiveSearchParams([GROUP_BY_PARAM_NAME, GROUP_TYPE_PARAM_NAME]);

  const { [DAILY_EXPENSES_BREAKDOWN_BY_PARAMETER_NAME]: dailyExpensesBreakdownByParameter } = useReactiveSearchParams(
    useMemo(() => [DAILY_EXPENSES_BREAKDOWN_BY_PARAMETER_NAME], [])
  );

  const { [DAILY_RESOURCE_COUNT_BREAKDOWN_BY_PARAMETER_NAME]: dailyResourceCountBreakdownByParameter } =
    useReactiveSearchParams(useMemo(() => [DAILY_RESOURCE_COUNT_BREAKDOWN_BY_PARAMETER_NAME], []));

  useEffect(() => {
    const selectedPerspective = validPerspectives[perspectiveNameSearchParameter];

    if (selectedPerspective) {
      const { filters, breakdownBy, breakdownData } = selectedPerspective;

      const filterParamsHasChanged = () => !areSearchParamsEqual(filtersQueryParams, filters.appliedFilters);

      const breakdownParamHasChanged = () => breakdownBy !== breakdownQueryParameter;

      const categorizeByHasChanged = () => {
        if (breakdownBy === CLEAN_EXPENSES_BREAKDOWN_TYPES.EXPENSES) {
          return breakdownData.breakdownBy !== dailyExpensesBreakdownByParameter;
        }
        if (breakdownBy === CLEAN_EXPENSES_BREAKDOWN_TYPES.RESOURCE_COUNT) {
          return breakdownData.breakdownBy !== dailyResourceCountBreakdownByParameter;
        }
        return false;
      };

      const groupByHasChanged = () => {
        if (breakdownBy === CLEAN_EXPENSES_BREAKDOWN_TYPES.EXPENSES) {
          return (
            groupByParameters.groupBy !== breakdownData.groupBy?.groupBy ||
            groupByParameters.groupType !== breakdownData.groupBy?.groupType
          );
        }
        return false;
      };

      const someParamHasChanged = [
        filterParamsHasChanged,
        breakdownParamHasChanged,
        categorizeByHasChanged,
        groupByHasChanged
      ].some((fn) => fn());

      if (someParamHasChanged) {
        removeQueryParam(RESOURCES_SELECTED_PERSPECTIVE_PARAMETER_NAME);
      }
    }
  }, [
    filtersQueryParams,
    perspectiveNameSearchParameter,
    validPerspectives,
    breakdownQueryParameter,
    dailyExpensesBreakdownByParameter,
    groupByParameters.groupBy,
    groupByParameters.groupType,
    dailyResourceCountBreakdownByParameter
  ]);

  const { useGet: useGetFilters } = AvailableFiltersService();

  const requestParams = useMemo(() => {
    const queryParams = getQueryParams();

    return {
      limit: Number(queryParams.limit || EXPENSES_LIMIT_FILTER_DEFAULT_VALUE),
      dateRange: {
        startDate: startDateTimestamp,
        endDate: endDateTimestamp
      },
      filters: { ...filtersQueryParams }
    };
  }, [filtersQueryParams, startDateTimestamp, endDateTimestamp]);

  const flatRequestParams = useMemo(
    () => ({
      ...requestParams.filters,
      ...requestParams.dateRange,
      limit: requestParams.limit
    }),
    [requestParams]
  );

  const getBreakdownDefinition = (breakdownName) => {
    const breakdown = BREAKDOWN_LINEAR_SELECTOR_ITEMS.find(({ name }) => name === breakdownName);

    if (breakdown) {
      return {
        name: breakdown.name,
        value: breakdown.value
      };
    }

    const { name, value } = getLength(BREAKDOWN_LINEAR_SELECTOR_ITEMS) > 0 ? BREAKDOWN_LINEAR_SELECTOR_ITEMS[0] : {};

    return {
      name,
      value
    };
  };

  const activeBreakdown = getBreakdownDefinition(breakdownQueryParameter);

  const { isLoading: isFilterValuesLoading, filters: filterValues } = useGetFilters(requestParams.dateRange);

  const onApply = (dateRange) => {
    updateQueryParams(dateRange);
  };

  const onFilterAdd = (newFilter) => {
    updateQueryParams(newFilter);
  };

  const onFilterDelete = (filterName, filterValue) => {
    const currentValue = filtersQueryParams[filterName];

    updateQueryParams({
      [filterName]: Array.isArray(currentValue) ? currentValue.filter((val) => val !== filterValue) : undefined
    });
  };

  const onFiltersDelete = () => {
    updateQueryParams(Object.fromEntries(Object.keys(filtersQueryParams).map((filterName) => [filterName, undefined])));
  };

  const onPerspectiveApply = (perspectiveName) => {
    navigate(
      getResourcesExpensesUrl({
        perspective: perspectiveName
      })
    );
  };

  return (
    <Resources
      startDateTimestamp={startDateTimestamp}
      endDateTimestamp={endDateTimestamp}
      filters={requestParams.filters}
      filterValues={filterValues}
      onApply={onApply}
      onFilterAdd={onFilterAdd}
      onFilterDelete={onFilterDelete}
      onFiltersDelete={onFiltersDelete}
      requestParams={flatRequestParams}
      isFilterValuesLoading={isFilterValuesLoading}
      activeBreakdown={activeBreakdown}
      selectedPerspectiveName={perspectiveNameSearchParameter}
      perspectives={validPerspectives}
      onPerspectiveApply={onPerspectiveApply}
      onBreakdownChange={({ name }) => {
        updateQueryParams({
          [RESOURCES_BREAKDOWN_BY_QUERY_PARAMETER_NAME]: name
        });
      }}
    />
  );
};

export default ResourcesContainer;
