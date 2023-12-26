import { lighten } from "@mui/material";
import { makeStyles } from "tss-react/mui";

export const WIDTH = 400;
export const WIDTH_STRING = `${WIDTH}px`;
const BORDER_ALPHA = 0.8;
const useStyles = makeStyles()((theme) => ({
  wrapper: {
    borderLeft: `1px solid ${lighten(theme.palette.info.main, BORDER_ALPHA)}`,
    height: "100%",
    width: WIDTH_STRING,
    position: "relative"
  },
  content: {
    width: WIDTH_STRING,
    position: "absolute",
    overflow: "auto",
    height: `calc(100% - ${theme.spacing(7)})`,
    top: theme.spacing(7),
    left: 0
  },
  loader: {
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    height: "100%"
  },
  toolbar: {
    height: theme.spacing(7),
    width: WIDTH_STRING
  }
}));

export default useStyles;
