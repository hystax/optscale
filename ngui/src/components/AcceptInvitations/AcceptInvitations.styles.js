import { makeStyles } from "tss-react/mui";
import { SPACING_1, SPACING_2 } from "utils/layouts";

const useStyles = makeStyles()((theme) => ({
  dashboardButton: {
    [theme.breakpoints.up("md")]: {
      position: "absolute",
      right: 40,
      bottom: 40
    },
    padding: theme.spacing(SPACING_2),
    "& > *:not(:last-child)": {
      marginRight: theme.spacing(SPACING_1)
    }
  }
}));

export default useStyles;
