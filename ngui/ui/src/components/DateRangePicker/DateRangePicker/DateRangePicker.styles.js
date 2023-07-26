import { makeStyles } from "tss-react/mui";

const useStyles = makeStyles()((theme) => ({
  header: {
    padding: "0.375rem"
  },
  headerItem: {
    flex: 1,
    textAlign: "center"
  },
  divider: {
    borderLeft: `1px solid ${theme.palette.action.focus}`,
    [theme.breakpoints.down("md")]: {
      display: "none"
    }
  },
  wrapper: {
    [theme.breakpoints.down("md")]: {
      display: "flex",
      justifyContent: "center",
      alignItems: "center"
    }
  },
  selectors: {
    [theme.breakpoints.down("md")]: {
      width: "100%"
    }
  }
}));

export default useStyles;
