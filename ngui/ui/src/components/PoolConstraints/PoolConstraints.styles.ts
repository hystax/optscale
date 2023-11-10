import { makeStyles } from "tss-react/mui";
import { SPACING_1, SPACING_2 } from "utils/layouts";

const useStyles = makeStyles()((theme) => ({
  item: {
    display: "inline-flex",
    marginRight: theme.spacing(SPACING_2),
    marginBottom: theme.spacing(SPACING_1)
  }
}));

export default useStyles;
