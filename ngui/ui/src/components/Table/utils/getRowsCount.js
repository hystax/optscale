const getCount = (tableData, getSubRows) =>
  tableData.reduce((acc, item) => {
    const subRows = getSubRows(item);

    return acc + 1 + (subRows ? getCount(subRows, getSubRows) : 0);
  }, 0);

export const getRowsCount = (tableData, { withExpanded, getSubRows }) => {
  if (withExpanded) {
    return getCount(tableData, getSubRows);
  }

  return tableData.length;
};
