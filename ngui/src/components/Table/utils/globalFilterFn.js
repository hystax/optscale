const getValue = (row, columnId) => {
  const value = row.getValue(columnId);

  if (typeof value === "number") {
    return String(value);
  }
  return value;
};

/**
 * https://github.com/TanStack/table/issues/4280
 */
export const globalFilterFn = (row, columnId, filterValue) => {
  const search = filterValue.toLowerCase();

  const value = getValue(row, columnId);

  return value?.toLowerCase().includes(search);
};
