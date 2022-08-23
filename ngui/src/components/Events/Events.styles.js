import { makeStyles } from "tss-react/mui";

const useStyles = makeStyles()((theme) => ({
  eventsWrapper: {
    display: "flex",
    position: "relative",
    height: `calc(100vh - ${theme.spacing(19.5)})`
  },
  events: {
    width: "100%",
    overflowY: "auto"
  },
  heading: {
    fontSize: theme.typography.pxToRem(15)
  },
  tableIcon: {
    verticalAlign: "bottom",
    paddingRight: "0.2rem"
  },
  successIcon: {
    color: theme.palette.success.main
  },
  infoIcon: {
    color: theme.palette.info.main
  },
  warningIcon: {
    color: theme.palette.warning.main
  },
  dateBlock: {
    paddingTop: "2rem"
  },
  accordionSummary: {
    minHeight: "0"
  },
  button: {
    position: "absolute",
    right: 0,
    marginTop: theme.spacing(4),
    marginRight: theme.spacing(8),
    zIndex: theme.zIndex.drawer,
    backgroundColor: theme.palette.primary.main,
    color: "white",
    "&:hover": {
      backgroundColor: theme.palette.primary.dark
    }
  }
}));

export default useStyles;
