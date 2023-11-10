import { memo } from "react";
import { TableCell } from "@mui/material";
import { CELL_EMPTY_VALUE } from "utils/tables";

const TableBodyCell = ({ cell, className }) => {
  const { style: cellStyle = {}, onRowCellClick, dataProductTourId, accessorKey, accessorFn } = cell.column.columnDef;

  const hasAccessor = accessorKey !== undefined || accessorFn !== undefined;

  const cellValue = cell.getValue();
  const hasCellValue = cellValue !== undefined;

  const onClick = typeof onRowCellClick === "function" ? (e) => onRowCellClick(e, cell.getContext()) : undefined;

  const getCellContent = () => {
    if (!hasAccessor || hasCellValue) {
      return typeof cell.column.columnDef.cell === "function"
        ? cell.column.columnDef.cell(cell.getContext())
        : cell.column.columnDef.cell;
    }

    return cell.column.columnDef.emptyValue || CELL_EMPTY_VALUE;
  };

  return (
    <TableCell key={cell.id} data-product-tour-id={dataProductTourId} onClick={onClick} className={className} style={cellStyle}>
      {getCellContent()}
    </TableCell>
  );
};

const MemoTableBodyCell = memo(TableBodyCell);

export { TableBodyCell, MemoTableBodyCell };
