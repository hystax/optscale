import { makeStyles } from "tss-react/mui";

const useStyles = makeStyles()((theme) => ({
  meetCustomersWrapper: {
    width: "100%"
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
    maxWidth: "120px",
    height: 54,
    width: "100%"
  },
  logoImage: {
    width: "100%"
  }
}));

export default useStyles;
