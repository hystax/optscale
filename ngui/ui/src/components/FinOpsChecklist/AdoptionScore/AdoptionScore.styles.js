import { makeStyles } from "tss-react/mui";
import { SPACING_1, SPACING_2 } from "utils/layouts";

const useStyles = makeStyles()((theme) => ({
  container: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    padding: theme.spacing(SPACING_2)
  },
  badge: {
    position: "relative",
    display: "inline-flex",
    marginTop: theme.spacing(SPACING_1)
  },
  circleBack: {
    position: "absolute",
    opacity: 0.2
  },
  scoreContainer: {
    position: "absolute",
    top: 0,
    left: 0,
    bottom: 0,
    right: 0,
    display: "flex",
    alignItems: "center",
    justifyContent: "center"
  }
}));

export default useStyles;
