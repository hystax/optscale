import { lighten } from "@mui/material/styles";
import { makeStyles } from "tss-react/mui";
import { SPACING_1, SPACING_2 } from "utils/layouts";

const ALPHA = 0.95;
const ALPHA_HOVER = 0.8;

const useStyles = makeStyles()((theme, color) => ({
  root: {
    minWidth: 150,
    maxWidth: 400,
    minHeight: 60,
    height: "100%",
    padding: 0,
    [theme.breakpoints.down("xl")]: {
      minWidth: 100
    },
    backgroundColor: lighten(color, ALPHA),
    color
  },
  button: {
    transition: "background-color 0.3s ease-in",
    cursor: "pointer",
    "&:hover": { backgroundColor: lighten(color, ALPHA_HOVER) }
  },
  content: {
    paddingTop: theme.spacing(SPACING_1),
    paddingLeft: theme.spacing(SPACING_2),
    display: "flex",
    height: "100%",
    flexDirection: "column",
    "&:last-child": {
      paddingBottom: theme.spacing(SPACING_1)
    }
  }
}));

export default useStyles;
