import { alpha } from "@mui/material/styles";

import { makeStyles } from "tss-react/mui";

const ALPHA = 0.5;

const useStyles = makeStyles()((theme, aboveDrawers = false) => ({
  backdrop: {
    zIndex: theme.zIndex.drawer + (aboveDrawers ? 1 : -1), // backdrop is one level below drawers by default. But in rare cases (whole app loader) — it is one level above
    backgroundColor: alpha(theme.palette.info.main, ALPHA),
    transform: "translateZ(0)" // fix for safari "jumpy" behaviour with transitions https://stackoverflow.com/a/37820050 + https://stackoverflow.com/q/57960955
  },
  content: {
    position: "absolute",
    alignItems: "flex-start",
    backgroundColor: alpha(theme.palette.common.white, 0.8)
  },
  contentLoader: {
    position: "absolute",
    backgroundColor: alpha(theme.palette.common.white, 0.8)
  }
}));

export default useStyles;
