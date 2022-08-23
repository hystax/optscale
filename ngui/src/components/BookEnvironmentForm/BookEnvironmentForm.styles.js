import { makeStyles } from "tss-react/mui";
import { SPACING_1, SPACING_3 } from "utils/layouts";

const useStyles = makeStyles()((theme) => ({
  fieldsWrapper: {
    marginTop: theme.spacing(SPACING_1),
    "& > *:not(:last-child)": {
      marginBottom: theme.spacing(SPACING_3)
    }
  }
}));

export default useStyles;
