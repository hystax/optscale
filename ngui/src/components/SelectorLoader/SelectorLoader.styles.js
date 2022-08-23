import { makeStyles } from "tss-react/mui";
import { SPACING_1 } from "utils/layouts";

const useStyles = makeStyles()((theme) => ({
  selector: {
    marginRight: theme.spacing(SPACING_1),
    minWidth: theme.spacing(30),
    "&:last-child": {
      marginRight: 0
    }
  }
}));

export default useStyles;
