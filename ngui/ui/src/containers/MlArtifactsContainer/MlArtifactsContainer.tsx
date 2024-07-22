import { ReactNode, useCallback, useEffect, useMemo, useState } from "react";
import { FormattedMessage } from "react-intl";
import Filters from "components/Filters";
import { ML_ARTIFACTS_FILTERS, ML_ARTIFACTS_FILTERS_NAMES } from "components/Filters/constants";
import TableLoader from "components/TableLoader";
import { useDebouncedValue } from "hooks/useDebouncedValue";
import MlArtifactsService, { Artifact } from "services/MlArtifactsService";
import { TASKS_BE_FILTER, TASKS_FILTER } from "utils/constants";
import {
  EN_FULL_FORMAT,
  SECONDS_IN_DAY,
  addYears,
  formatUTC,
  getEndOfTodayInUTCinSeconds,
  getStartOfTodayInUTCinSeconds,
  millisecondsToSeconds,
  secondsToMilliseconds,
  subYears
} from "utils/datetime";
import { getQueryParams, updateQueryParams } from "utils/network";

export type Pagination = {
  pageCount: number;
  pageIndex: number;
  onPageIndexChange: (newPageIndex: number) => void;
  totalRows: number;
  pageSize: number;
};

export type Search = {
  onChange: (value: string) => void;
  value: string;
};

export type RangeFilter = {
  filterComponentProps: {
    min: number;
    max: number;
    step: number;
    filterFn: (originalRow: unknown, range: [number, number]) => boolean;
    title: (range: [number, number]) => ReactNode;
  };
  manualFilterDefinition: {
    onChange: (value: [number, number]) => void;
    range: readonly [number, number];
  };
};

export type TasksFilter = {
  definition: Filters;
  onChange: (filter: { name: string; value: string[] }) => void;
  onFilterDelete: (filter: { filterName: string; filterValue: string }) => void;
  onFiltersDelete: () => void;
};

type MlArtifactsContainerProps = {
  runId?: string | string[];
  tasks?: { id: string; name: string }[];
  isLoading?: boolean;
  render: (props: {
    artifacts: Artifact[];
    pagination: Pagination;
    search: Search;
    rangeFilter: RangeFilter;
    tasksFilter: TasksFilter;
  }) => ReactNode;
};

const PAGE_SIZE = 50;
const DEFAULT_PAGE_INDEX = 0;
const SEARCH_QUERY_PARAM_NAME = "search";
const PAGE_QUERY_PARAM_NAME = "page";
const START_DATE_QUERY_PARAM_NAME = "startDate";
const END_DATE_QUERY_PARAM_NAME = "endDate";

const getDefaultSearchValue = () => {
  const { [SEARCH_QUERY_PARAM_NAME]: search = "" } = getQueryParams();
  return String(search);
};

const getDefaultPageIndexValue = () => {
  const { [PAGE_QUERY_PARAM_NAME]: page } = getQueryParams();

  const numberPage = Number(page);

  return Number.isInteger(numberPage) && numberPage >= 0 ? numberPage - 1 : DEFAULT_PAGE_INDEX;
};

const getRangeQueryParams = (minRange: number, maxRange: number) => {
  const { [START_DATE_QUERY_PARAM_NAME]: startDate, [END_DATE_QUERY_PARAM_NAME]: endDate } = getQueryParams();

  const startNumber = Number(startDate);
  const endNumber = Number(endDate);

  if (Number.isInteger(startNumber) && Number.isInteger(endNumber)) {
    return [Math.max(startNumber, minRange), Math.min(endNumber, maxRange)] as const;
  }

  return [minRange, maxRange] as const;
};

const MlArtifactsContainer = ({ runId, tasks = [], isLoading = false, render }: MlArtifactsContainerProps) => {
  const { useGet } = MlArtifactsService();

  const [pageIndex, setPageIndex] = useState(getDefaultPageIndexValue());
  const [searchValue, setSearchValue] = useState(getDefaultSearchValue());

  const minRange = millisecondsToSeconds(+subYears(secondsToMilliseconds(getStartOfTodayInUTCinSeconds()), 1));
  const maxRange = millisecondsToSeconds(+addYears(secondsToMilliseconds(getEndOfTodayInUTCinSeconds()), 1));

  const [range, setRange] = useState(getRangeQueryParams(minRange, maxRange));

  const onDebouncedRangeChange = useCallback(() => {
    setPageIndex(DEFAULT_PAGE_INDEX);
  }, []);
  const debouncedRange = useDebouncedValue(range, {
    onDebouncedValueChange: onDebouncedRangeChange
  });

  const filterValues = {
    [TASKS_BE_FILTER]: tasks.map(({ id, name }) => ({
      value: id,
      name
    }))
  };

  const [appliedFilters, setAppliedFilters] = useState<Record<string, string | string[] | undefined>>(() => {
    const queryParams = getQueryParams();

    return ML_ARTIFACTS_FILTERS_NAMES.reduce(
      (params, queryKey) => ({
        ...params,
        [queryKey]: queryParams[queryKey]
      }),
      {}
    );
  });

  const onAppliedFiltersChange = (newAppliedFiltersValue) => {
    setPageIndex(DEFAULT_PAGE_INDEX);
    setAppliedFilters(newAppliedFiltersValue);
  };

  const params = useMemo(
    () => ({
      limit: PAGE_SIZE,
      startFrom: pageIndex * PAGE_SIZE,
      runId,
      textLike: searchValue,
      createdAtGt: debouncedRange[0],
      createdAtLt: debouncedRange[1],
      taskId: appliedFilters[TASKS_FILTER]
    }),
    [pageIndex, runId, searchValue, debouncedRange, appliedFilters]
  );

  const onSearchChange = (newSearch: string) => {
    setPageIndex(DEFAULT_PAGE_INDEX);
    setSearchValue(newSearch);
  };

  const onPageIndexChange = (newPageIndex: number) => {
    setPageIndex(newPageIndex);
  };

  const onRangeChange = (newRange: [number, number]) => {
    setRange(newRange);
  };

  useEffect(() => {
    updateQueryParams({
      [SEARCH_QUERY_PARAM_NAME]: searchValue,
      [PAGE_QUERY_PARAM_NAME]: pageIndex + 1,
      [START_DATE_QUERY_PARAM_NAME]: debouncedRange[0],
      [END_DATE_QUERY_PARAM_NAME]: debouncedRange[1],
      [TASKS_FILTER]: appliedFilters[TASKS_FILTER]
    });
  }, [pageIndex, debouncedRange, searchValue, appliedFilters]);

  const { isLoading: isGetArtifactsLoading, data } = useGet(params);

  const totalArtifactsCount = data?.total_count ?? 0;

  const pageCount = totalArtifactsCount ? Math.ceil(totalArtifactsCount / PAGE_SIZE) : 1;

  return isLoading || isGetArtifactsLoading ? (
    <TableLoader columnsCounter={4} showHeader />
  ) : (
    render({
      artifacts: data?.artifacts ?? [],
      pagination: {
        pageCount,
        pageIndex,
        onPageIndexChange,
        totalRows: totalArtifactsCount,
        pageSize: PAGE_SIZE
      },
      search: {
        value: searchValue,
        onChange: onSearchChange
      },
      rangeFilter: {
        filterComponentProps: {
          min: minRange,
          max: maxRange,
          step: SECONDS_IN_DAY,
          filterFn: () => true,
          title: (currentRange) => (
            <FormattedMessage
              id="timerange"
              values={{
                from: formatUTC(currentRange[0], EN_FULL_FORMAT),
                to: formatUTC(currentRange[1], EN_FULL_FORMAT)
              }}
            />
          )
        },
        manualFilterDefinition: {
          onChange: onRangeChange,
          range
        }
      },
      tasksFilter: {
        definition: new Filters({
          filters: ML_ARTIFACTS_FILTERS,
          filterValues,
          appliedFilters
        }),
        onChange: ({ name, value }) => {
          onAppliedFiltersChange((currentlyAppliedFilters) => ({ ...currentlyAppliedFilters, [name]: value }));
        },
        onFilterDelete: (filterToDelete) => {
          onAppliedFiltersChange((currentlyAppliedFilters) => {
            const currentFilterValues = currentlyAppliedFilters[filterToDelete.filterName];
            const isArrayFilterValues = currentFilterValues;

            return {
              ...currentlyAppliedFilters,
              [filterToDelete.filterName]: isArrayFilterValues
                ? currentFilterValues.filter((val) => val !== filterToDelete.filterValue)
                : undefined
            };
          });
        },
        onFiltersDelete: () => {
          onAppliedFiltersChange((currentlyAppliedFilters) =>
            Object.entries(currentlyAppliedFilters).reduce(
              (newRequestParams, [filterName]) => ({
                ...newRequestParams,
                [filterName]: undefined
              }),
              {}
            )
          );
        }
      }
    })
  );
};

export default MlArtifactsContainer;
