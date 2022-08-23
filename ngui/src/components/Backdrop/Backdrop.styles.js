import { alpha } from "@mui/material/styles";

import { makeStyles } from "tss-react/mui";

const ALPHA = 0.5;

const useStyles = makeStyles()((theme) => ({
  backdrop: {
    zIndex: theme.zIndex.drawer + 1,
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
