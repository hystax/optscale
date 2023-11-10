import { TableCell } from "@mui/material";
import useStyles from "./TableFooterCell.styles";

const TableFooterCell = ({ footerContext }) => {
  const { classes } = useStyles();

  const content =
    typeof footerContext.column.columnDef.footer === "function"
      ? footerContext.column.columnDef.footer(footerContext.getContext())
      : footerContext.column.columnDef.footer;

  return (
    <TableCell className={classes.cell} colSpan={footerContext.colSpan} rowSpan={footerContext.rowSpan}>
      <strong>{content}</strong>
    </TableCell>
  );
};

export default TableFooterCell;
