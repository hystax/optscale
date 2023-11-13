import { makeStyles } from "tss-react/mui";

const useStyles = makeStyles()((theme) => ({
  insideBrackets: {
    fontSize: theme.typography.pxToRem(18),
    lineHeight: theme.spacing(1.25)
  }
}));

export default useStyles;
