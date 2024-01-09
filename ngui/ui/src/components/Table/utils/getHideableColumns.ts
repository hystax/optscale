export const getHideableColumns = (tableContext) => tableContext.getAllLeafColumns().filter((column) => column.getCanHide());
