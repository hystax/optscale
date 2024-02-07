import { makeStyles } from "tss-react/mui";

const useStyles = makeStyles()((theme) => ({
  questionMark: {
    fontSize: theme.typography.body1.fontSize,
    color: "inherit"
  }
}));

export default useStyles;
