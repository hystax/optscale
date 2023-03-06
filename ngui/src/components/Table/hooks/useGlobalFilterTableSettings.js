import { useCallback, useState } from "react";
import { getFilteredRowModel } from "@tanstack/react-table";
import { getQueryParams, updateQueryParams } from "utils/network";
import { getSearchQueryKey } from "utils/tables";
import { globalFilterFn, handleChange } from "../utils";

const addSearchToQueryParams = (searchKey, searchText) => {
  updateQueryParams({ [searchKey]: searchText });
};

const getInitialSearchValue = (key) => {
  const { [key]: search = "" } = getQueryParams();
  return search;
};

export const useGlobalFilterTableSettings = ({ queryParamPrefix }) => {
  const searchQueryKey = getSearchQueryKey(queryParamPrefix);

  const [globalFilter, setGlobalFilter] = useState(getInitialSearchValue(searchQueryKey));

  const onSearchChange = useCallback(
    (newSearchValue, { tableContext }) => {
      setGlobalFilter(newSearchValue);
      addSearchToQueryParams(searchQueryKey, newSearchValue);

      tableContext.setPageIndex(0);
    },
    [searchQueryKey]
  );

  return {
    state: {
      globalFilter
    },
    tableOptions: {
      getFilteredRowModel: getFilteredRowModel(),
      globalFilterFn,
      onGlobalFilterChange: handleChange(globalFilter, setGlobalFilter)
    },
    onSearchChange
  };
};
