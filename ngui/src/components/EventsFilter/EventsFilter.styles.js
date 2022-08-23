import { makeStyles } from "tss-react/mui";

const useStyles = makeStyles()((theme) => ({
  drawerPaper: {
    position: "relative",
    whiteSpace: "nowrap",
    backgroundColor: "inherit",
    border: "none",
    transition: theme.transitions.create("width", {
      easing: theme.transitions.easing.sharp,
      duration: theme.transitions.duration.enteringScreen
    })
  },
  drawerPaperClose: {
    overflowX: "hidden",
    display: "none",
    transition: theme.transitions.create("width", {
      easing: theme.transitions.easing.sharp,
      duration: theme.transitions.duration.leavingScreen
    }),
    [theme.breakpoints.up("sm")]: {
      width: theme.spacing(9)
    }
  }
}));

export default useStyles;
