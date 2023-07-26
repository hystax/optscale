import { lighten } from "@mui/material";
import { makeStyles } from "tss-react/mui";
import { SPACING_2 } from "utils/layouts";

const ALPHA = 0.9;
const useStyles = makeStyles()((theme) => ({
  item: {
    position: "relative", // for bar positioning
    padding: "5px",
    ":not(:last-child)": { marginBottom: theme.spacing(SPACING_2) }
  },
  itemContent: {
    position: "relative", // to set item content above bar (which is absolute)
    flexGrow: 1
  },
  flexRow: {
    display: "flex",
    flexDirection: "row",
    width: "100%",
    alignItems: "center"
  },
  bar: {
    position: "absolute",
    top: 0,
    left: 0,
    height: "100%",
    backgroundColor: lighten(theme.palette.lightBlue.main, ALPHA),
    borderRadius: "4px"
  }
}));

export default useStyles;
