import { makeStyles } from "tss-react/mui";
import { SPACING_2 } from "utils/layouts";

const useStyles = makeStyles()((theme) => ({
  bar: {
    backgroundColor: "white",
    color: "inherit",
    boxShadow: "none"
  },
  isPage: {
    paddingRight: theme.spacing(SPACING_2),
    paddingLeft: theme.spacing(SPACING_2)
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
  },
  link: {
    textDecoration: "none",
    "&:hover": {
      textDecoration: "none"
    },
    color: "inherit"
  }
}));

export default useStyles;
