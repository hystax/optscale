import { makeStyles } from "tss-react/mui";
import { SPACING_2 } from "utils/layouts";

const useStyles = makeStyles()((theme) => ({
  constraintWrapper: {
    display: "inline-flex",
    marginRight: theme.spacing(SPACING_2)
  }
}));

export default useStyles;
