import { makeStyles } from "tss-react/mui";

const useStyles = makeStyles()((theme) => ({
  resourceSpecific: {
    color: theme.palette.warning.dark
  },
  card: {
    boxShadow: "none",
    overflow: "visible",
    width: 360,
    [theme.breakpoints.down("xl")]: {
      width: 340
    },
    [theme.breakpoints.down("lg")]: {
      width: 320
    },
    [theme.breakpoints.down("sm")]: {
      width: "auto"
    }
  },
  cardHeader: {
    paddingBottom: 0
  }
}));

export default useStyles;
