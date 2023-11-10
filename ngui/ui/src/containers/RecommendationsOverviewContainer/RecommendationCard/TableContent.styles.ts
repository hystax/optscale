import { makeStyles } from "tss-react/mui";
import { SPACING_1 } from "utils/layouts";

const useStyles = makeStyles()((theme, columnsCount) => ({
  grid: {
    justifyContent: "space-between",
    display: "grid",
    gridTemplateColumns: `repeat(${columnsCount}, auto)`,
    gap: theme.spacing(SPACING_1)
  }
}));

export default useStyles;
