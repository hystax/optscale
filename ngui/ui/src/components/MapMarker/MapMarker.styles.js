import { makeStyles } from "tss-react/mui";
import { SPACING_1 } from "utils/layouts";

const useStyles = makeStyles()((theme) => ({
  markerBase: {
    position: "absolute",
    display: "flex",
    flexDirection: "column",
    justifyContent: "center",
    alignItems: "center",
    color: theme.palette.text.primary,
    backgroundColor: theme.palette.common.white,
    overflow: "hidden",
    fontWeight: "bold",
    cursor: "pointer",
    borderWidth: "4px",
    borderStyle: "solid",
    "&:hover": {
      zIndex: theme.zIndex.drawer
    }
  },
  marker: {
    borderRadius: "50% 50% 50% 0",
    transform: "rotate(-45deg)"
  },
  cluster: {
    borderRadius: "50%",
    borderColor: theme.palette.divider,
    transform: "translate(-50%, -100%)"
  },
  markerTooltip: {
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
    marginLeft: 0
  },
  markerTooltipWrapper: {
    position: "absolute",
    willChange: "transform",
    display: "none",
    zIndex: theme.zIndex.tooltip,
    transform: "translate3d(-50%, -0.5rem, 0px)"
  },
  markerTooltipWrapperShow: {
    display: "block"
  },
  tooltipItem: {
    "&:not(:last-child)": {
      borderBottom: "1px solid",
      borderBottomColor: theme.palette.divider,
      paddingBottom: theme.spacing(SPACING_1),
      marginBottom: theme.spacing(SPACING_1)
    }
  }
}));

export default useStyles;
