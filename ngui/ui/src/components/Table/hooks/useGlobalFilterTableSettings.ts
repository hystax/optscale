import { useCallback, useMemo, useState } from "react";
import { getFilteredRowModel } from "@tanstack/react-table";
import { getQueryParams, updateQueryParams } from "utils/network";
import { getSearchQueryKey } from "utils/tables";
import { globalFilterFn } from "../utils";

const addSearchToQueryParams = (searchKey, searchText) => {
  updateQueryParams({ [searchKey]: searchText });
};

const getInitialSearchValue = (key) => {
  const { [key]: search = "" } = getQueryParams();
  return search;
};

const useSearch = ({ queryParamPrefix, enableSearchQueryParam = true }) => {
  const searchQueryKey = enableSearchQueryParam ? getSearchQueryKey(queryParamPrefix) : undefined;

  const [search, setSearch] = useState(() => {
    if (enableSearchQueryParam) {
      return getInitialSearchValue(searchQueryKey);
    }
    return "";
  });

  const onSearchChange = useCallback(
    (newSearchValue, { tableContext }) => {
      setSearch(newSearchValue);
      if (enableSearchQueryParam) {
        addSearchToQueryParams(searchQueryKey, newSearchValue);
      }

      tableContext.setPageIndex(0);
    },
    [searchQueryKey, enableSearchQueryParam]
  );

  return {
    search,
    onSearchChange
  };
};

const useRange = ({ rangeFilter }) => {
  const [range, setRange] = useState(rangeFilter ? [rangeFilter.min, rangeFilter.max] : [-Infinity, Infinity]);

  const onRangeChange = useCallback((newRange, { tableContext }) => {
    setRange(newRange);
    tableContext.setPageIndex(0);
  }, []);

  return {
    range,
    onRangeChange
  };
};

export const useGlobalFilterTableSettings = ({
  withSearch,
  queryParamPrefix,
  enableSearchQueryParam,
  columns,
  rangeFilter
}) => {
  const { search, onSearchChange } = useSearch({
    queryParamPrefix,
    enableSearchQueryParam
  });

  const { range, onRangeChange } = useRange({
    rangeFilter
  });

  const globalFilter = useMemo(
    () => ({
      search,
      range
    }),
    [range, search]
  );

  return {
    state: {
      globalFilter
    },
    tableOptions: {
      getFilteredRowModel: getFilteredRowModel(),
      globalFilterFn: globalFilterFn({ columns, withSearch, rangeFilter })
    },
    onSearchChange,
    onRangeChange
  };
};
