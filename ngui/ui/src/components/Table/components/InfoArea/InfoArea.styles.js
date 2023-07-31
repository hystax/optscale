import { makeStyles } from "tss-react/mui";

const useStyles = makeStyles()((theme) => ({
  infoWrapper: {
    display: "flex",
    flexGrow: 1,
    alignItems: "center",
    width: "max-content",
    marginTop: theme.spacing(1),
    marginBottom: theme.spacing(1),
    "& > *": {
      "&:not(:last-child)": {
        marginRight: theme.spacing(1)
      }
    }
  }
}));

export default useStyles;
