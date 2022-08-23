import { makeStyles } from "tss-react/mui";

const useStyles = makeStyles()((theme) => ({
  success: {
    color: theme.palette.success.main
  },
  error: {
    color: theme.palette.error.main
  }
}));

export default useStyles;
