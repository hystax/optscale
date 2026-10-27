import { ReactNode, useCallback, useState } from "react";
import type { Table as TanStackTable } from "@tanstack/react-table";

type TableRangeFilterConfig<TData> = {
  min: number;
  max: number;
  step: number;
  title: (rangeValue: [number, number]) => ReactNode;
  filterFn: (originalRow: TData, range: [number, number]) => boolean;
};

type UseRangeParams<TData> = {
  rangeFilter: TableRangeFilterConfig<TData> | undefined;
};

export const useRange = <TData>({ rangeFilter }: UseRangeParams<TData>) => {
  const [range, setRange] = useState<[number, number]>(() =>
    rangeFilter ? [rangeFilter.min, rangeFilter.max] : [-Infinity, Infinity]
  );

  const onRangeChange = useCallback((newRange: [number, number], { tableContext }: { tableContext: TanStackTable<TData> }) => {
    setRange(newRange);
    tableContext.setPageIndex(0);
  }, []);

  return {
    range,
    onRangeChange,
  };
};
