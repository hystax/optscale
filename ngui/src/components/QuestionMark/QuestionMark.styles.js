import { makeStyles } from "tss-react/mui";
import { SPACING_1 } from "utils/layouts";

const useStyles = makeStyles()((theme) => ({
  questionMark: {
    cursor: "default",
    color: theme.palette.secondary.main,
    marginLeft: theme.spacing(SPACING_1),
    "&:hover": {
      backgroundColor: "inherit"
    }
  },
  rightSide: {
    paddingRight: 0
  }
}));

export default useStyles;
