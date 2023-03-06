import { makeStyles } from "tss-react/mui";

const useStyles = makeStyles()((theme, { wrapperHeight }) => ({
  wrapper: {
    height: theme.spacing(wrapperHeight),
    marginTop: theme.spacing(2),
    position: "relative",
    zIndex: 1
  },
  contentWrapper: {
    position: "absolute",
    zIndex: -1,
    width: "100%",
    height: "100%",
    left: 0,
    top: 0
  }
}));

export default useStyles;
