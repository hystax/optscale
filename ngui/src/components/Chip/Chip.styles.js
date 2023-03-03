import { makeStyles } from "tss-react/mui";

const useStyles = makeStyles()(() => ({
  chip: {
    maxWidth: "100%"
  },
  uppercase: {
    textTransform: "uppercase"
  }
}));

export default useStyles;
