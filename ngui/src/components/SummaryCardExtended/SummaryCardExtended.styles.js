import { makeStyles } from "tss-react/mui";

const useStyles = makeStyles()((theme) => ({
  root: {
    maxWidth: 340,
    height: 80,
    borderLeft: `0.5rem ${theme.palette.info.main} solid`
  },
  content: {
    display: "flex",
    flexWrap: "wrap"
  },
  extendedValue: {
    display: "flex",
    flexBasis: "100%",
    maxWidth: "100%",
    height: 35,
    justifyContent: "flex-start",
    alignItems: "center"
  },
  valueWrapper: {
    display: "flex",
    alignItems: "center",
    flex: "1 1 50%",
    maxWidth: "50%",
    [theme.breakpoints.down("sm")]: {
      flexBasis: "40%",
      maxWidth: "40%"
    }
  },
  marginLeft: {
    marginLeft: theme.spacing(2)
  },
  marginRight: {
    marginRight: theme.spacing(2)
  },
  relativeValue: {
    marginRight: theme.spacing(1)
  },
  relativeValueCaption: {
    fontSize: "0.7rem"
  },
  skeleton: {
    maxWidth: "max-content"
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
