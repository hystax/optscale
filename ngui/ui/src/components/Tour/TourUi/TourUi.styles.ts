import { makeStyles } from "tss-react/mui";

const useStyles = makeStyles()((theme) => ({
  mask: {
    zIndex: theme.zIndex.drawer + 1,
    position: "fixed",
    boxShadow: "0 0 0 9999px rgba(0, 0, 0, 0.5)",
    transition: "all 0.1s ease-out"
  },
  invisibleBackgroundEventsCapturer: {
    zIndex: theme.zIndex.drawer + 1,
    position: "fixed",
    top: 0,
    left: 0,
    width: "100vw",
    height: "100vh"
  }
}));

export default useStyles;
