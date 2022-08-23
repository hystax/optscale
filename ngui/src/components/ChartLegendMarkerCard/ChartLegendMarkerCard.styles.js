import { makeStyles } from "tss-react/mui";

const useStyles = makeStyles()((theme, { markerColor }) => ({
  wrapper: {
    height: theme.spacing(5),
    display: "flex"
  },
  content: {
    display: "flex",
    flexDirection: "column",
    justifyContent: "space-between"
  },
  marker: {
    height: "100%",
    width: theme.spacing(0.5),
    borderRadius: theme.spacing(0.5),
    marginRight: theme.spacing(0.5)
  },
  markerColor: {
    backgroundColor: markerColor
  }
}));

export default useStyles;
