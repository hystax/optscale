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

const searchFilter = ({ row, filterValue, columnId, columns }) => {
  const { search } = filterValue;

  const columnDef = getColumnById(columnId, columns);

  if (typeof columnDef?.searchFn === "function") {
    return columnDef.searchFn(row.getValue(columnId), search, {
      row,
      columnId
    });
  }

  const value = getValue(row, columnId);

  return value?.toLocaleLowerCase().includes(search.toLocaleLowerCase());
};

export const globalFilterFn =
  ({ columns, withSearch, rangeFilter }) =>
  (row, columnId, filterValue) =>
    (withSearch ? searchFilter({ row, filterValue, columnId, columns }) : true) &&
    (rangeFilter ? rangeFilter.filterFn(row.original, filterValue.range) : true);
