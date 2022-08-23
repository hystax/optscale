import { makeStyles } from "tss-react/mui";

const useStyles = makeStyles()((theme) => ({
  infoWrapper: {
    display: "flex",
    flexGrow: 1,
    alignItems: "center",
    width: "max-content",
    "& > *": {
      "&:not(:last-child)": {
        marginRight: theme.spacing(1)
      }
    }
  },
  wrapper: {
    width: "100%",
    display: "flex",
    alignItems: "center",
    justifyContent: "flex-end",
    paddingBottom: theme.spacing(1),
    borderBottom: "1px solid rgba(0, 0, 0, 0.12)",
    flexWrap: "wrap"
  },
  actionsWrapper: {
    display: "flex",
    alignItems: "center",
    maxWidth: "100%",
    "& > *": {
      "&:not(:last-child)": {
        marginRight: theme.spacing(1)
      }
    }
  },
  searchInput: {
    [theme.breakpoints.down("sm")]: {
      flex: 1
    }
  }
}));

export default useStyles;
