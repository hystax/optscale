import { makeStyles } from "tss-react/mui";

const useStyles = makeStyles()((theme) => ({
  title: {
    color: theme.palette.common.white
  },
  logosWrapper: {
    width: "100%",
    display: "flex",
    [theme.breakpoints.down("md")]: {
      flexWrap: "wrap"
    },
    justifyContent: "center"
  },
  logoWrapper: {
    width: 35,
    margin: theme.spacing(2)
  },
  logoImage: {
    width: "100%"
  }
}));

export default useStyles;
