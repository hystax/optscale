import { makeStyles } from "tss-react/mui";

const useStyles = makeStyles()((theme) => ({
  fullWidthHeight: {
    height: "100%",
    width: "100%"
  },
  clearFiltersButton: {
    marginLeft: theme.spacing(1)
  },
  wrapper: {
    "& line.highlight": {
      stroke: theme.palette.primary.light,
      strokeWidth: 4
    },
    /**
     * Disable drag-n-drop for vertical lines (dimensions)
     */
    "& text.axis-title": {
      pointerEvents: "none !important"
    }
  }
}));

export default useStyles;
