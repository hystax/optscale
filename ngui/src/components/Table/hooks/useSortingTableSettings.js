import { getSortedRowModel } from "@tanstack/react-table";

export const useSortingTableSettings = () => ({
  tableOptions: {
    getSortedRowModel: getSortedRowModel(),
    enableSortingRemoval: false // disable the unsorted state if sorting on the column has been applied at least once
  }
});
