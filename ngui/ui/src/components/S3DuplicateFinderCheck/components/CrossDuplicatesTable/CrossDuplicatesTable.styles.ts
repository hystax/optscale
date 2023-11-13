import { makeStyles } from "tss-react/mui";

const useStyles = makeStyles()((theme) => ({
  selectedFromCellBorder: {
    borderTop: `2px solid ${theme.palette.info.main}`,
    borderBottom: `2px solid ${theme.palette.info.main}`,
    borderLeft: `2px solid ${theme.palette.info.main}`
  },
  selectedToCellBorder: {
    borderTop: `2px solid ${theme.palette.info.main}`,
    borderRight: `2px solid ${theme.palette.info.main}`,
    borderLeft: `2px solid ${theme.palette.info.main}`
  },
  selectedCellBorders: {
    border: `2px solid ${theme.palette.info.main}`
  },
  cellInRowPathBorders: {
    borderTop: `2px solid ${theme.palette.info.main}`,
    borderBottom: `2px solid ${theme.palette.info.main}`
  },
  cellInColumnPathBorders: {
    borderLeft: `2px solid ${theme.palette.info.main}`,
    borderRight: `2px solid ${theme.palette.info.main}`
  }
}));

export default useStyles;
