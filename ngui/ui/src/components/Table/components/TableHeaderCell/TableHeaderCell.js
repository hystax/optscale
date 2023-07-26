import React from "react";
import { TableCell, TableSortLabel } from "@mui/material";
import { SORTING_ORDER } from "utils/constants";

const Cell = ({ children, colSpan, rowSpan, style, onClick }) => (
  <TableCell colSpan={colSpan} rowSpan={rowSpan} style={style} onClick={onClick}>
    {children ? <strong>{children}</strong> : null}
  </TableCell>
);

const TableHeaderCell = ({ headerContext }) => {
  const { style: cellStyle = {} } = headerContext.column.columnDef;

  const getCellContent = () => {
    if (headerContext.isPlaceholder) {
      return null;
    }

    if (headerContext.column.getCanSort()) {
      const appliedSortDirection = headerContext.column.getIsSorted();

      const isSorted = [SORTING_ORDER.ASC, SORTING_ORDER.DESC].includes(appliedSortDirection);

      const labelSortDirection = isSorted ? appliedSortDirection : SORTING_ORDER.ASC;

      const renderSortLabel = (label) => (
        <TableSortLabel
          active={isSorted}
          direction={labelSortDirection}
          onClick={headerContext.column.getToggleSortingHandler()}
        >
          {label}
        </TableSortLabel>
      );

      return typeof headerContext.column.columnDef.header === "function"
        ? headerContext.column.columnDef.header({
            ...headerContext.getContext(),
            renderSortLabel
          })
        : renderSortLabel(headerContext.column.columnDef.header);
    }

    return typeof headerContext.column.columnDef.header === "function"
      ? headerContext.column.columnDef.header(headerContext.getContext())
      : headerContext.column.columnDef.header;
  };

  return (
    <Cell style={cellStyle} colSpan={headerContext.colSpan} rowSpan={headerContext.rowSpan}>
      {getCellContent()}
    </Cell>
  );
};

export default TableHeaderCell;
