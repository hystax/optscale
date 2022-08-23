import { makeStyles } from "tss-react/mui";

const useStyles = makeStyles()((theme) => ({
  helperText: {
    marginTop: theme.spacing(1),
    marginBottom: theme.spacing(0.5)
  }
}));

export default useStyles;
