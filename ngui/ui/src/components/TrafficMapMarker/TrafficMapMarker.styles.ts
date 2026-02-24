import { makeStyles } from "tss-react/mui";
import { MAP_MARKER_FONT_SIZE_IN_PX } from "../../utils/fonts";

const useStyles = makeStyles()((theme) => ({
  marker: {
    "&:hover": {
      zIndex: theme.zIndex.drawer,
    },
    display: "flex",
    cursor: "pointer",
    color: theme.palette.text.primary,
    fontWeight: "bold",
    borderRadius: "4px",
    overflow: "hidden",
    justifyContent: "center",
    alignItems: "center",
    border: `2px solid ${theme.palette.info.light}`,
    backgroundColor: theme.palette.common.white,
    position: "absolute",
    fontSize: theme.typography.pxToRem(MAP_MARKER_FONT_SIZE_IN_PX),
  },
  markerTop: {
    transform: "translate(-50%, -100%)",
  },
  markerBottom: {
    transform: "translate(-50%, 0)",
  },
}));

export default useStyles;
