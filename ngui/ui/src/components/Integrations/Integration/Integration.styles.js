import { makeStyles } from "tss-react/mui";

const useStyles = makeStyles()((theme) => ({
  blocksWrapper: {
    "& > *:not(:last-child)": {
      marginBottom: theme.spacing(1)
    }
  },
  paper: {
    padding: theme.spacing(2)
  }
}));

export default useStyles;
