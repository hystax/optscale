import { useCallback, useState } from "react";
import type { Table as TanStackTable } from "@tanstack/react-table";
import { getSearchParams, updateSearchParams } from "utils/network";
import { getSearchQueryKey } from "utils/tables";

type UseSearchParams = {
  queryParamPrefix?: string;
  enableSearchQueryParam?: boolean;
};

const getInitialSearchValue = (key: string): string => {
  const { [key]: search = "" } = getSearchParams({
    parseNumbers: false,
    parseBooleans: false,
  });

  return String(search ?? "");
};

const addSearchToQueryParams = (searchKey: string, searchText: string) => {
  updateSearchParams({ [searchKey]: searchText });
};

export const useSearch = <TData>({ queryParamPrefix, enableSearchQueryParam = true }: UseSearchParams) => {
  const searchQueryKey = enableSearchQueryParam ? getSearchQueryKey(queryParamPrefix ?? "") : undefined;

  const [search, setSearch] = useState(() => {
    if (!enableSearchQueryParam) {
      return "";
    }
    return getInitialSearchValue(getSearchQueryKey(queryParamPrefix ?? ""));
  });

  const onSearchChange = useCallback(
    (newSearchValue: string, { tableContext }: { tableContext: TanStackTable<TData> }) => {
      setSearch(newSearchValue);
      if (enableSearchQueryParam && searchQueryKey !== undefined) {
        addSearchToQueryParams(searchQueryKey, newSearchValue);
      }

      tableContext.setPageIndex(0);
    },
    [searchQueryKey, enableSearchQueryParam]
  );

  return {
    search,
    onSearchChange,
  };
};
