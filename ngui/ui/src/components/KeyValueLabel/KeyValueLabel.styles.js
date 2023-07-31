import { makeStyles } from "tss-react/mui";

const useStyles = makeStyles()((_, { flexWrap }) => ({
  root: {
    display: "flex",
    flexWrap,
    alignItems: "center"
  }
}));

export default useStyles;
