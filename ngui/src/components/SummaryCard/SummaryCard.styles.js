import { makeStyles } from "tss-react/mui";

const useStyles = makeStyles()((theme) => ({
  root: {
    width: 265,
    height: 80,
    borderLeft: `0.5rem ${theme.palette.info.main} solid`
  },
  content: {
    display: "flex",
    flexWrap: "wrap"
  },
  valueWrapper: {
    display: "flex",
    alignItems: "center",
    flexBasis: "100%",
    height: 45,
    overflow: "hidden"
  },
  primary: {
    borderLeftColor: theme.palette.primary.main
  },
  secondary: {
    borderLeftColor: theme.palette.secondary.main
  },
  success: {
    borderLeftColor: theme.palette.success.main
  },
  error: {
    borderLeftColor: theme.palette.error.main
  },
  warning: {
    borderLeftColor: theme.palette.warning.main
  }
}));

export default useStyles;
