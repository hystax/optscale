import { makeStyles } from "tss-react/mui";
import { SPACING_1, SPACING_2 } from "utils/layouts";

const useStyles = makeStyles()((theme) => ({
  page: {
    backgroundColor: theme.palette.background.paper,
    flexGrow: 1,
    padding: theme.spacing(SPACING_2),
    paddingTop: theme.spacing(SPACING_1)
  }
}));

export default useStyles;
