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
  infoIcon: {
    color: theme.palette.info.main
  },
  warningIcon: {
    color: theme.palette.warning.main
  },
  dateBlock: {
    paddingTop: "2rem"
  }
}));

export default useStyles;
