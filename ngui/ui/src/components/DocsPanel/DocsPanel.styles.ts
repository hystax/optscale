import { lighten } from "@mui/material";
import { makeStyles } from "tss-react/mui";

const BORDER_ALPHA = 0.8;

const useStyles = makeStyles()((theme) => ({
  wrapper: {
    height: "100%",
    position: "relative"
  },
  content: {
    borderLeft: `1px solid ${lighten(theme.palette.info.main, BORDER_ALPHA)}`,
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
    height: theme.spacing(7)
  }
}));

export default useStyles;
