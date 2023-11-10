import { makeStyles } from "tss-react/mui";

const useStyles = makeStyles()(() => ({
  text: {
    textTransform: "uppercase"
  },
  textWrapper: {
    padding: 0
  }
}));

export default useStyles;
