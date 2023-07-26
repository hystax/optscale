import { makeStyles } from "tss-react/mui";

const useStyles = makeStyles()((theme) => ({
  buttonProgress: {
    margin: theme.spacing(1)
  },
  tooltipSpan: {
    width: "max-content"
  }
}));

export default useStyles;
