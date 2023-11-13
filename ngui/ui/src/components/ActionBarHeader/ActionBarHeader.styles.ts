import { makeStyles } from "tss-react/mui";

const useStyles = makeStyles()((theme) => ({
  logo: {
    width: "100%",
    height: "100%"
  },
  logoWrapper: {
    width: "2rem",
    [theme.breakpoints.up("sm")]: {
      width: "2.5rem"
    }
  },
  title: {
    wordBreak: "break-all"
  }
}));

export default useStyles;
