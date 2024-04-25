import { sortObjects } from "utils/arrays";
import { DEFAULT_PAGE_KEY, DEFAULT_SEARCH_KEY } from "utils/constants";

export const RESOURCE_ID_COLUMN_CELL_STYLE = Object.freeze({
  wordBreak: "break-word",
  minWidth: 250
});

export const getDefaultTableData = <T, K extends keyof T>(sourceArray: T[], field: K, sortType: "desc" | "asc" = "desc") =>
  sortObjects({ array: sourceArray, field, type: sortType });

export const getPaginationQueryKey = (label: string) => (label ? `${label}Page` : DEFAULT_PAGE_KEY);
export const getSearchQueryKey = (label: string) => (label ? `${label}Search` : DEFAULT_SEARCH_KEY);

export const CELL_EMPTY_VALUE = "-";
