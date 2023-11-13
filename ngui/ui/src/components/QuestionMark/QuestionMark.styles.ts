import { makeStyles } from "tss-react/mui";
import { SPACING_1 } from "utils/layouts";

const useStyles = makeStyles()((theme) => ({
  questionMark: {
    cursor: "default",
    "&:hover": {
      backgroundColor: "inherit"
    }
  },
  leftMargin: {
    marginLeft: theme.spacing(SPACING_1)
  },
  rightSide: {
    paddingRight: 0
  }
}));

export default useStyles;
