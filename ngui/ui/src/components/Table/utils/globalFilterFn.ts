/**
 * https://github.com/TanStack/table/issues/4280
 */
const getValue = (row, columnId) => {
  const value = row.getValue(columnId);

  if (typeof value === "number") {
    return String(value);
  }
  return value;
};

const getColumnById = (columnId, columns) => columns.find(({ id, accessorKey }) => [id, accessorKey].includes(columnId));

export const globalFilterFn = (columns) => (row, columnId, filterValue) => {
  const value = getValue(row, columnId);

  const columnDef = getColumnById(columnId, columns);

  if (typeof columnDef?.globalFilterFn === "function") {
    return columnDef?.globalFilterFn(row.getValue(columnId), filterValue, {
      row,
      columnId
    });
  }

  const search = filterValue.toLocaleLowerCase();

  return value?.toLocaleLowerCase().includes(search);
};
