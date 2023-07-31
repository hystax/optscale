import { makeStyles } from "tss-react/mui";

const useStyles = makeStyles()((theme, { mainColor, secondaryColor, backgroundColor }) => ({
  wrapper: {
    position: "relative",
    display: "flex",
    alignItems: "center",
    justifyContent: "center"
  },
  progress: {
    height: "0.5rem",
    borderRadius: "0.3rem",
    width: "100%"
  },
  bar1Buffer: {
    backgroundColor: mainColor
  },
  bar2Buffer: {
    backgroundColor: secondaryColor
  },
  dashed: {
    backgroundColor,
    backgroundImage: "none",
    animation: "none"
  }
}));

export default useStyles;
