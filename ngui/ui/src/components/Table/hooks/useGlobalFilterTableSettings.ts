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

const useSearch = ({ withSearch, queryParamPrefix }) => {
  const searchQueryKey = getSearchQueryKey(queryParamPrefix);

  const [search, setSearch] = useState(withSearch ? getInitialSearchValue(searchQueryKey) : "");

  const onSearchChange = useCallback(
    (newSearchValue, { tableContext }) => {
      setSearch(newSearchValue);
      addSearchToQueryParams(searchQueryKey, newSearchValue);

      tableContext.setPageIndex(0);
    },
    [searchQueryKey]
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

export const useGlobalFilterTableSettings = ({ queryParamPrefix, columns, withSearch, rangeFilter }) => {
  const { search, onSearchChange } = useSearch({
    withSearch,
    queryParamPrefix
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
