import { makeStyles } from "tss-react/mui";
import { SPACING_1 } from "utils/layouts";

const useStyles = makeStyles()((theme) => ({
  tooltip: {
    border: "1px solid",
    backgroundColor: theme.palette.common.white,
    paddingTop: theme.spacing(0.5),
    paddingBottom: theme.spacing(0.5),
    paddingRight: theme.spacing(SPACING_1),
    paddingLeft: theme.spacing(SPACING_1),
    width: "max-content",
    maxWidth: "15rem",
    borderRadius: theme.spacing(0.5),
    marginTop: theme.spacing(1.7),
    marginBottom: theme.spacing(1.7),
    marginRight: 0,
    marginLeft: 0,
    position: "absolute",
    fontSize: "10px",
    pointerEvents: "none"
  },
  legend: {
    height: "14px",
    width: "200px",
    backgroundColor: "rgb(167,225,241)",
    backgroundImage:
      "linear-gradient(90deg, rgba(167,225,241,1) 0%, rgba(108,211,245,1) 35%, rgba(164,222,52,1) 63%, rgba(236,235,26,1) 74%, rgba(252,179,21,1) 84%, rgba(241,36,38,1) 100%);"
  }
}));

export default useStyles;
