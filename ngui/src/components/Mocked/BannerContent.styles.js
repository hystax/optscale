import { makeStyles } from "tss-react/mui";

const useStyles = makeStyles()((theme) => ({
  buttonMargin: {
    marginBottom: theme.spacing(1)
  },
  bold: {
    fontWeight: "bold"
  },
  icon: {
    width: "4rem",
    height: "4rem",
    marginTop: `calc(-2rem - ${theme.spacing(2)})`,
    marginBottom: theme.spacing(1)
  },
  buttonsWrapper: {
    display: "flex",
    flexDirection: "column",
    "& >*": {
      "&:not(:last-child)": {
        marginBottom: theme.spacing(1)
      }
    }
  },
  buttonsWrapperMargin: {
    marginBottom: theme.spacing(1)
  }
}));

export default useStyles;
