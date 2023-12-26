import { lighten } from "@mui/material/styles";

import { makeStyles } from "tss-react/mui";
import { SPACING_1 } from "utils/layouts";

const ALPHA = 0.8;

const useStyles = makeStyles()((theme, { height }) => ({
  wrapper: {
    position: "relative",
    display: "inline-flex",
    alignItems: "center",
    justifyContent: "center",
    height
  },
  progress: {
    position: "absolute",
    borderRadius: "0.3rem",
    width: "100%",
    height: "100%",
    backgroundColor: lighten(theme.palette.common.black, 0.95)
  },
  valuePrimary: {
    color: theme.palette.primary.main
  },
  barPrimary: {
    backgroundColor: lighten(theme.palette.primary.main, ALPHA)
  },

  valueSuccess: {
    color: theme.palette.success.main
  },
  barSuccess: {
    backgroundColor: lighten(theme.palette.success.main, ALPHA)
  },

  valueError: {
    color: theme.palette.error.main
  },
  barError: {
    backgroundColor: lighten(theme.palette.error.main, ALPHA)
  },

  valueWarning: {
    color: theme.palette.warning.main
  },
  barWarning: {
    backgroundColor: lighten(theme.palette.warning.main, ALPHA)
  },
  valueWrapper: {
    width: "100%",
    zIndex: "1",
    textAlign: "center",
    paddingLeft: theme.spacing(SPACING_1),
    paddingRight: theme.spacing(SPACING_1),
    fontWeight: "bold"
  }
}));

export default useStyles;
