import { makeStyles } from "tss-react/mui";

const useStyles = makeStyles()(() => ({
  switchWrapper: {
    position: "relative"
  },
  absoluteSwitch: {
    position: "absolute",
    transform: "translateY(-50%)",
    top: "50%",
    left: "0"
  }
}));

export default useStyles;
