import { makeStyles } from "tss-react/mui";

const useStyles = makeStyles()(() => ({
  container: {
    overflowY: "auto",
    paddingLeft: "0",
    paddingRight: "0",
    margin: "auto",
    maxWidth: "none"
  }
}));

export default useStyles;
