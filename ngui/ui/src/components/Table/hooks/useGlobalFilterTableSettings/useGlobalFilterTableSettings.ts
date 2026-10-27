import { useMemo } from "react";
import type { ReactNode } from "react";
import type { ColumnDef, FilterFn, Row, Table as TanStackTable } from "@tanstack/react-table";
import { getFilteredRowModel } from "@tanstack/react-table";
import { globalFilterFn } from "../../utils";
import { useRange } from "./useRange";
import { useSearch } from "./useSearch";

type GlobalFilterColumnDef<TData> = ColumnDef<TData, unknown> & {
  searchFn?: (cellValue: unknown, search: string, context: { row: Row<TData>; columnId: string }) => boolean;
};

type TableRangeFilterConfig<TData> = {
  min: number;
  max: number;
  step: number;
  title: (rangeValue: [number, number]) => ReactNode;
  filterFn: (originalRow: TData, range: [number, number]) => boolean;
};

type UseGlobalFilterTableSettingsParams<TData> = {
  columns: GlobalFilterColumnDef<TData>[];
  queryParamPrefix?: string;
  withSearch?: boolean;
  enableSearchQueryParam?: boolean;
  rangeFilter?: TableRangeFilterConfig<TData>;
};

type UseGlobalFilterTableSettingsResult<TData> = {
  state: {
    globalFilter: {
      search: string;
      range: [number, number];
    };
  };
  tableOptions: {
    getFilteredRowModel: ReturnType<typeof getFilteredRowModel>;
    globalFilterFn: FilterFn<TData>;
  };
  onSearchChange: (newSearchValue: string, options: { tableContext: TanStackTable<TData> }) => void;
  onRangeChange: (newRange: [number, number], options: { tableContext: TanStackTable<TData> }) => void;
};

export const useGlobalFilterTableSettings = <TData>({
  columns,
  withSearch,
  queryParamPrefix,
  enableSearchQueryParam,
  rangeFilter,
}: UseGlobalFilterTableSettingsParams<TData>): UseGlobalFilterTableSettingsResult<TData> => {
  const { search, onSearchChange } = useSearch<TData>({
    queryParamPrefix,
    enableSearchQueryParam,
  });

  const { range, onRangeChange } = useRange<TData>({
    rangeFilter,
  });

  const globalFilter = useMemo(
    () => ({
      search,
      range,
    }),
    [range, search]
  );

  return {
    state: {
      globalFilter,
    },
    tableOptions: {
      getFilteredRowModel: getFilteredRowModel(),
      globalFilterFn: globalFilterFn({ columns, withSearch, rangeFilter }),
    },
    onSearchChange,
    onRangeChange,
  };
};
