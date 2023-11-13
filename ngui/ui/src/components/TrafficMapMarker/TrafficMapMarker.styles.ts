import { makeStyles } from "tss-react/mui";
import { SPACING_1 } from "utils/layouts";
import { MAP_MARKER_FONT_SIZE_IN_PX } from "../../utils/fonts";

const useStyles = makeStyles()((theme) => ({
  marker: {
    "&:hover": {
      zIndex: theme.zIndex.drawer
    },
    display: "flex",
    cursor: "pointer",
    color: theme.palette.text.primary,
    fontWeight: "bold",
    borderRadius: "4px",
    overflow: "hidden",
    justifyContent: "center",
    alignItems: "center",
    width: 140,
    height: 30,
    border: `2px solid ${theme.palette.info.light}`,
    backgroundColor: theme.palette.common.white,
    position: "absolute",
    fontSize: theme.typography.pxToRem(MAP_MARKER_FONT_SIZE_IN_PX)
  },
  markerTop: {
    left: -70,
    top: -30
  },
  markerBottom: {
    left: -70,
    top: 0
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
  }
}));

export default useStyles;
