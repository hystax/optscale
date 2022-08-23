import { makeStyles } from "tss-react/mui";
import { SPACING_4 } from "utils/layouts";

const useStyles = makeStyles()((theme) => ({
  bar: {
    backgroundColor: "white",
    color: "inherit",
    boxShadow: "none"
  },
  isPage: {
    borderBottom: "1px solid rgba(0, 0, 0, 0.12)",
    paddingRight: theme.spacing(SPACING_4)
  },
  itemsWrapper: {
    whiteSpace: "nowrap",
    display: "flex",
    alignItems: "center"
  },
  margin: {
    "& > *": {
      marginRight: theme.spacing(1),
      "&:last-child": {
        marginRight: 0
      }
    }
  },
  actions: {
    display: "inline-flex"
  }
}));

export default useStyles;
