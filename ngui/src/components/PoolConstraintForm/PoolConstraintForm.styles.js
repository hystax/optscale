import { makeStyles } from "tss-react/mui";

const useStyles = makeStyles()((theme) => ({
  card: {
    boxShadow: "none",
    overflow: "visible",
    width: 340,
    height: 170,
    [theme.breakpoints.down("xl")]: {
      width: 320,
      height: 160
    },
    [theme.breakpoints.down("lg")]: {
      width: 300,
      height: 150
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
