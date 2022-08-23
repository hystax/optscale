import { makeStyles } from "tss-react/mui";

const useStyles = makeStyles()(() => ({
  root: {
    maxWidth: 450
  },
  skipButton: {
    marginRight: "auto"
  },
  backButton: {
    marginLeft: "auto"
  },
  nextButton: {
    marginLeft: "auto"
  }
}));

export default useStyles;
