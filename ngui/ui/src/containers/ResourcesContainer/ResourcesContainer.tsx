import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import Resources from "components/Resources";
import { FILTER_CONFIGS } from "components/Resources/filterConfigs";
import { RANGE_DATES } from "containers/RangePickerFormContainer/reducer";
import { useAvailableFiltersQuery } from "graphql/__generated__/hooks/restapi";
import { useOrganizationPerspectives } from "hooks/coreData/useOrganizationPerspectives";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { useReactiveSearchParam } from "hooks/useReactiveSearchParam";
import { useRootData } from "hooks/useRootData";
import {
  DAILY_EXPENSES_BREAKDOWN_BY_PARAMETER_NAME,
  DAILY_RESOURCE_COUNT_BREAKDOWN_BY_PARAMETER_NAME,
  getResourcesExpensesUrl,
  GROUP_BY_PARAM_NAME,
  GROUP_TYPE_PARAM_NAME,
  RESOURCES_BREAKDOWN_BY_QUERY_PARAMETER_NAME,
  RESOURCES_SELECTED_PERSPECTIVE_PARAMETER_NAME,
} from "urls";
import {
  DATE_RANGE_TYPE,
  EXPENSES_LIMIT_FILTER_DEFAULT_VALUE,
  CLEAN_EXPENSES_BREAKDOWN_TYPES,
  CLEAN_EXPENSES_BREAKDOWN_TYPES_LIST,
} from "utils/constants";
import { getCurrentMonthRange } from "utils/datetime";
import { getSearchParams, removeSearchParam, updateSearchParams } from "utils/network";

const useDateRange = () => {
  const { rootData: storageRangeDates = {} } = useRootData(RANGE_DATES, (result = {}) => result[DATE_RANGE_TYPE.RESOURCES]);

  const [dateRange, setDateRange] = useState(() => {
    const allSearchParams = getSearchParams();
    const { startOfMonth: defaultStartDate, today: defaultEndDate } = getCurrentMonthRange(true);

    const getStartDate = () => {
      if (allSearchParams.startDate) {
        return allSearchParams.startDate;
      }

      if (storageRangeDates.startDate) {
        return storageRangeDates.startDate;
      }

      return defaultStartDate;
    };

    const getEndDate = () => {
      if (allSearchParams.endDate) {
        return allSearchParams.endDate;
      }

      if (storageRangeDates.endDate) {
        return storageRangeDates.endDate;
      }

      return defaultEndDate;
    };

    return {
      startDate: Number(getStartDate()),
      endDate: Number(getEndDate()),
    };
  });

  return [dateRange, setDateRange] as const;
};

const useListenForPerspectiveChange = (selectedPerspectiveDefinition) => {
  const dailyExpensesBreakdownBy = useReactiveSearchParam(DAILY_EXPENSES_BREAKDOWN_BY_PARAMETER_NAME);
  const dailyResourceCountBreakdownBy = useReactiveSearchParam(DAILY_RESOURCE_COUNT_BREAKDOWN_BY_PARAMETER_NAME);
  const groupBy = useReactiveSearchParam(GROUP_BY_PARAM_NAME);
  const groupType = useReactiveSearchParam(GROUP_TYPE_PARAM_NAME);

  useEffect(() => {
    if (selectedPerspectiveDefinition) {
      const { breakdownBy, breakdownData } = selectedPerspectiveDefinition;

      const categorizeByHasChanged = () => {
        if (breakdownBy === CLEAN_EXPENSES_BREAKDOWN_TYPES.EXPENSES) {
          return breakdownData.breakdownBy !== dailyExpensesBreakdownBy;
        }
        if (breakdownBy === CLEAN_EXPENSES_BREAKDOWN_TYPES.RESOURCE_COUNT) {
          return breakdownData.breakdownBy !== dailyResourceCountBreakdownBy;
        }
        return false;
      };

      const groupByHasChanged = () => {
        if (breakdownBy === CLEAN_EXPENSES_BREAKDOWN_TYPES.EXPENSES) {
          return groupBy !== breakdownData.groupBy?.groupBy || groupType !== breakdownData.groupBy?.groupType;
        }
        return false;
      };

      const someParamHasChanged = [categorizeByHasChanged, groupByHasChanged].some((fn) => fn());

      if (someParamHasChanged) {
        removeSearchParam(RESOURCES_SELECTED_PERSPECTIVE_PARAMETER_NAME);
      }
    }
  }, [dailyExpensesBreakdownBy, dailyResourceCountBreakdownBy, groupBy, groupType, selectedPerspectiveDefinition]);
};

const ResourcesContainer = () => {
  const { organizationId } = useOrganizationInfo();

  const navigate = useNavigate();

  const [appliedFilters, setAppliedFilters] = useState(() =>
    Object.fromEntries(
      Object.values(FILTER_CONFIGS).map((filterConfig) => {
        const { getValuesFromSearchParams } = filterConfig;

        return [filterConfig.id, getValuesFromSearchParams()];
      })
    )
  );

  const perspectiveName = useReactiveSearchParam(RESOURCES_SELECTED_PERSPECTIVE_PARAMETER_NAME);

  const { validPerspectives } = useOrganizationPerspectives();

  const [dateRange, setDateRange] = useDateRange();

  const [breakdownByState, setBreakdownByState] = useState(() => {
    const { [RESOURCES_BREAKDOWN_BY_QUERY_PARAMETER_NAME]: breakdownBy } = getSearchParams();

    if (CLEAN_EXPENSES_BREAKDOWN_TYPES_LIST.includes(breakdownBy)) {
      return breakdownBy;
    }

    return CLEAN_EXPENSES_BREAKDOWN_TYPES.EXPENSES;
  });

  const selectedPerspectiveDefinition = useMemo(() => validPerspectives[perspectiveName], [validPerspectives, perspectiveName]);

  useListenForPerspectiveChange(selectedPerspectiveDefinition);

  const requestParams = useMemo(() => {
    const queryParams = getSearchParams();

    const apiFilterParams = Object.entries(appliedFilters).reduce((acc, [key, value]) => {
      const config = FILTER_CONFIGS[key];

      if (!config) {
        return acc;
      }

      return {
        ...acc,
        ...config.transformers.toApi(value),
      };
    }, {});

    return {
      limit: Number(queryParams.limit || EXPENSES_LIMIT_FILTER_DEFAULT_VALUE),
      dateRange: {
        startDate: dateRange.startDate,
        endDate: dateRange.endDate,
      },
      filters: apiFilterParams,
    };
  }, [dateRange, appliedFilters]);

  const flatRequestParams = useMemo(
    () => ({
      ...requestParams.filters,
      ...requestParams.dateRange,
      limit: requestParams.limit,
    }),
    [requestParams]
  );

  useEffect(() => {
    updateSearchParams(requestParams.dateRange);
  }, [requestParams.dateRange]);

  const { data: availableFiltersData, loading: isAvailableFiltersLoading } = useAvailableFiltersQuery({
    variables: {
      organizationId,
      params: {
        start_date: dateRange.startDate,
        end_date: dateRange.endDate,
      },
    },
  });

  const onApplyDateRange = (dateRange) => {
    setDateRange(dateRange);
  };

  const onPerspectiveApply = (newPerspectiveName) => {
    navigate(
      getResourcesExpensesUrl({
        perspective: newPerspectiveName,
      })
    );
  };

  return (
    <Resources
      startDateTimestamp={dateRange.startDate}
      endDateTimestamp={dateRange.endDate}
      filterValues={availableFiltersData?.availableFilters ?? {}}
      onApply={onApplyDateRange}
      requestParams={flatRequestParams}
      isFilterValuesLoading={isAvailableFiltersLoading}
      activeBreakdown={breakdownByState}
      onBreakdownChange={(breakdownBy) => {
        if (selectedPerspectiveDefinition) {
          removeSearchParam(RESOURCES_SELECTED_PERSPECTIVE_PARAMETER_NAME);
        }

        setBreakdownByState(breakdownBy);
      }}
      selectedPerspectiveName={perspectiveName}
      perspectives={validPerspectives}
      onPerspectiveApply={onPerspectiveApply}
      appliedFilters={appliedFilters}
      onAppliedFiltersChange={(newFilters) => {
        if (selectedPerspectiveDefinition) {
          removeSearchParam(RESOURCES_SELECTED_PERSPECTIVE_PARAMETER_NAME);
        }

        const queryParamsToUpdate = Object.entries(newFilters).reduce((acc, [key, value]) => {
          const filterConfig = FILTER_CONFIGS[key];
          if (filterConfig) {
            return {
              ...acc,
              ...filterConfig.transformers.toApi(value),
            };
          }
          return acc;
        }, {});

        updateSearchParams(queryParamsToUpdate);

        setAppliedFilters((prev) => ({
          ...prev,
          ...newFilters,
        }));
      }}
    />
  );
};

export default ResourcesContainer;
