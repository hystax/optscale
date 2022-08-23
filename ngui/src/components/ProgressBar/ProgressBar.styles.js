import { lighten } from "@mui/material/styles";

import { makeStyles } from "tss-react/mui";

const ALPHA = 0.7;

const useStyles = makeStyles()((theme) => ({
  wrapper: {
    position: "relative",
    display: "flex",
    alignItems: "center",
    justifyContent: "center"
  },
  progress: {
    height: "2rem",
    borderRadius: "0.3rem",
    width: "100%",
    backgroundColor: "white"
  },
  progressPrimary: {
    border: `2px solid ${theme.palette.primary.main}`
  },
  progressSuccess: {
    border: `2px solid ${theme.palette.success.main}`
  },
  progressError: {
    border: `2px solid ${theme.palette.error.main}`
  },
  progressWarning: {
    border: `2px solid ${theme.palette.warning.main}`
  },
  barPrimary: {
    backgroundColor: lighten(theme.palette.primary.main, ALPHA)
  },
  barSuccess: {
    backgroundColor: lighten(theme.palette.success.main, ALPHA)
  },
  barError: {
    backgroundColor: lighten(theme.palette.error.main, ALPHA)
  },
  barWarning: {
    backgroundColor: lighten(theme.palette.warning.main, ALPHA)
  },
  valueWrapper: {
    position: "absolute"
  }
}));

export default useStyles;
