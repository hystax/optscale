import { makeStyles } from "tss-react/mui";

const useStyles = makeStyles()((theme) => ({
  resourceSpecific: {
    color: theme.palette.warning.dark
  }
}));

export default useStyles;
