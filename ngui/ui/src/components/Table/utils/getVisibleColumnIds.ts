export const getVisibleColumnIds = (tableContext): string[] =>
  tableContext
    .getAllLeafColumns()
    .filter((column) => column.getIsVisible())
    .map(({ id }) => id);
