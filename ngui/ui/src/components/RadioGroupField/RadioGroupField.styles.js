import { makeStyles } from "tss-react/mui";

const useStyles = makeStyles()((theme) => ({
  radioGroup: {
    paddingLeft: theme.spacing(1.75)
  },
  fullWidthSkeleton: {
    maxWidth: "100%"
  }
}));

export default useStyles;
