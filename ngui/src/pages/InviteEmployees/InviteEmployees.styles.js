import { makeStyles } from "tss-react/mui";

const useStyles = makeStyles()((theme) => ({
  wrapper: {
    position: "relative"
  },
  buttonProgress: {
    color: theme.palette.success.main,
    position: "absolute",
    top: "50%",
    left: "50%",
    marginTop: theme.spacing(-1.5),
    marginLeft: theme.spacing(-2.3)
  }
}));

export default useStyles;
