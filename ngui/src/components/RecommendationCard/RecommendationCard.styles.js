import { lighten } from "@mui/system";
import { makeStyles } from "tss-react/mui";
import { SPACING_2 } from "utils/layouts";

const ALPHA = 0.95;
const useStyles = makeStyles()((theme, color) => ({
  // full height card with info-border or background color
  card: {
    height: "100%",
    border: !color ? `1px solid ${lighten(theme.palette.info.main, 0.8)}` : "",
    backgroundColor: color ? lighten(theme.palette[color].main, ALPHA) : ""
  },
  // card content with spaces between its items
  content: {
    display: "flex",
    flexDirection: "column",
    justifyContent: "space-between",
    height: "100%"
  },
  // card header with space between title+description and counters
  header: {
    display: "flex",
    flexDirection: "row",
    justifyContent: "space-between",
    marginBottom: theme.spacing(SPACING_2)
  },
  // minimal space between card title and counters
  title: {
    marginRight: theme.spacing(SPACING_2)
  }
}));

export default useStyles;
