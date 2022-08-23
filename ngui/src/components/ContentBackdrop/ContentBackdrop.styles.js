import { makeStyles } from "tss-react/mui";

const useStyles = makeStyles()((theme) => ({
  buttonMargin: {
    marginBottom: theme.spacing(1)
  },
  bold: {
    fontWeight: "bold"
  },
  root: {
    position: "fixed",
    display: "flex",
    maxWidth: "450px",
    width: "calc(100% - 20px)",
    alignItems: "center",
    flexDirection: "column",
    top: "50%",
    left: "50%",
    zIndex: theme.zIndex.drawer + 2,
    transform: "translate(-50%, -50%)",
    padding: theme.spacing(2)
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
