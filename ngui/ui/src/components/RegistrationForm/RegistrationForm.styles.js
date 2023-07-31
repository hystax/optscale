import { makeStyles } from "tss-react/mui";

const useStyles = makeStyles()((theme) => ({
  registerButtonWrapper: {
    margin: theme.spacing(3, 0, 2)
  },
  registerButton: {
    marginBottom: theme.spacing(1)
  }
}));

export default useStyles;
