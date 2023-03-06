import { keyframes } from "tss-react";
import { makeStyles } from "tss-react/mui";

const useStyles = makeStyles()((theme) => ({
  root: {
    maxWidth: 450,
    position: "fixed",
    zIndex: 9998,
    transition: "all 0.1s ease-out"
  },
  skipButton: {
    marginRight: "auto"
  },
  backButton: {
    marginLeft: "auto"
  },
  nextButton: {
    marginLeft: "auto"
  },
  arrowContainer: {
    position: "absolute",
    zIndex: theme.zIndex.drawer + 1,
    transition: "opacity 0.2s ease-in",
    display: "flex",
    flexDirection: "row",
    alignItems: "center",
    left: "50%",
    bottom: 0,
    transform: "translate(-50%, calc(100% + 10px))"
  },
  arrow: {
    color: theme.palette.common.white,
    animation: `${keyframes`
            0%, 100% {
              transform: translateY(5px);
            }
            50% {
              transform: translateY(-5px);
            }
            `} 1s infinite ease-in-out`
  },
  hidden: {
    opacity: 0
  },
  visible: {
    opacity: 1
  }
}));

export default useStyles;
