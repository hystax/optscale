import { makeStyles } from "tss-react/mui";

const useStyles = makeStyles()((theme) => ({
  tooltip: {
    "& > *:not(:last-child)": {
      marginBottom: theme.spacing(1.5)
    }
  }
}));

export default useStyles;
