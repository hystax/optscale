import { makeStyles } from "tss-react/mui";
import { SPACING_1 } from "utils/layouts";

const useStyles = makeStyles()((theme) => ({
  wrapper: {
    display: "flex",
    paddingTop: `${SPACING_1}rem`,
    width: "100%",
    "& .Mui-selected": {
      background: theme.palette.secondary.main,
      color: theme.palette.secondary.contrastText,
      "&:hover": {
        backgroundColor: theme.palette.secondary.light
      }
    }
  },
  right: {
    justifyContent: "flex-end"
  },
  center: {
    justifyContent: "center"
  },
  left: {
    justifyContent: "flex-start"
  }
}));

export default useStyles;
