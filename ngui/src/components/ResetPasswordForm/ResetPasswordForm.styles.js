import { makeStyles } from "tss-react/mui";

const useStyles = makeStyles()((theme) => ({
  submitButtonWrapper: {
    margin: theme.spacing(3, 0, 2)
  },
  successIcon: {
    fontSize: "5rem",
    color: theme.palette.success.main,
    marginBottom: theme.spacing(1)
  }
}));

export default useStyles;
