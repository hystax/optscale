import { makeStyles } from "tss-react/mui";

const useStyles = makeStyles()((theme) => ({
  warningText: {
    color: theme.palette.warning.main
  }
}));

export default useStyles;
