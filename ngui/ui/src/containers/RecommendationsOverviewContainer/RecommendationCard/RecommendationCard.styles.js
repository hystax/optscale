import { lighten } from "@mui/system";
import { makeStyles } from "tss-react/mui";
import { SPACING_2 } from "utils/layouts";

const ALPHA = 0.95;
const useStyles = makeStyles()((theme, color) => ({
  card: {
    display: "flex",
    flexDirection: "column",
    justifyContent: "space-between",
    maxHeight: "450px",
    border: !color ? `1px solid ${lighten(theme.palette.info.main, 0.8)}` : "",
    backgroundColor: color ? lighten(theme.palette[color].main, ALPHA) : ""
  },
  content: {
    display: "flex",
    flexDirection: "column",
    justifyContent: "space-between"
  },
  description: {
    marginBottom: theme.spacing(SPACING_2)
  },
  actions: {
    justifyContent: "space-between",
    paddingLeft: theme.spacing(SPACING_2),
    paddingRight: theme.spacing(SPACING_2)
  }
}));

export default useStyles;
