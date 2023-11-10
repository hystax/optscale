import { lighten } from "@mui/material";
import { makeStyles } from "tss-react/mui";

const useStyles = makeStyles()((theme, options) => ({
  progressBarPaper: {
    position: "relative"
  },
  progressBar: {
    position: "absolute",
    height: "100%",
    backgroundColor: lighten(theme.palette[options.progressBar.color].main, 0.9),
    width: options.progressBar.width
  },
  possibleSavingsTitle: {
    display: "flex",
    alignItems: "center",
    justifyContent: "center"
  }
}));

export default useStyles;
