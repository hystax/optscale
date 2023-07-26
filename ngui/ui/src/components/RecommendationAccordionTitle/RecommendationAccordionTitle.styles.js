import { makeStyles } from "tss-react/mui";

const useStyles = makeStyles()((theme) => ({
  text: {
    display: "flex",
    [theme.breakpoints.up("md")]: {
      flexDirection: "row"
    },
    flexDirection: "column"
  },
  divider: {
    [theme.breakpoints.up("md")]: {
      display: "inherit"
    },
    display: "none",
    marginRight: theme.spacing(1),
    marginLeft: theme.spacing(1)
  }
}));

export default useStyles;
