import { getColumnId } from "../utils";

export const useInitialSortingState = (columns) => {
  const defSortColumn = columns.find((column) => column.defaultSort);

  const initialSorting = defSortColumn ? [{ id: getColumnId(defSortColumn), desc: defSortColumn.defaultSort === "desc" }] : [];

  return initialSorting;
};
