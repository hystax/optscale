import { makeStyles } from "tss-react/mui";
import { SPACING_2 } from "utils/layouts";

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
    wordBreak: "break-all",
    paddingTop: theme.spacing(SPACING_2),
    paddingBottom: theme.spacing(SPACING_2)
  }
}));

export default useStyles;
