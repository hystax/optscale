import { makeStyles } from "tss-react/mui";

const useStyles = makeStyles()((theme) => ({
  alertDialogText: {
    marginTop: theme.spacing(1),
    marginBottom: theme.spacing(0.5)
  },
  alertDialogHeader: {
    padding: "16px 24px 5px 24px"
  }
}));

export default useStyles;
