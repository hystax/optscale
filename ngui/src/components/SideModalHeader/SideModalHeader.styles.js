import { makeStyles } from "tss-react/mui";

const useStyles = makeStyles()((theme) => ({
  title: {
    flexGrow: 1
  },
  headerPrimary: {
    color: theme.palette.primary.contrastText,
    backgroundColor: theme.palette.primary.main
  },
  headerSuccess: {
    color: theme.palette.success.contrastText,
    backgroundColor: theme.palette.success.main
  },
  headerInfo: {
    color: theme.palette.info.dark,
    backgroundColor: theme.palette.info.light
  },
  headerError: {
    color: theme.palette.error.contrastText,
    backgroundColor: theme.palette.error.main
  }
}));

export default useStyles;
