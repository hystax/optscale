import { makeStyles } from "tss-react/mui";
import { SPACING_1 } from "utils/layouts";

const useStyles = makeStyles()((theme) => ({
  questionMark: {
    fontSize: theme.typography.body1.fontSize,
    color: "inherit"
  },
  icon: {
    marginLeft: theme.spacing(SPACING_1),
    display: "flex",
    alignItems: "center"
  }
}));

export default useStyles;
