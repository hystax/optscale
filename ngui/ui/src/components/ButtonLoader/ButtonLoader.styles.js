import { makeStyles } from "tss-react/mui";

const useStyles = makeStyles()((theme) => ({
  buttonProgress: {
    position: "absolute",
    top: "50%",
    left: "50%",
    marginTop: theme.spacing(-1.5),
    marginLeft: theme.spacing(-1.5)
  },
  primaryCircularProgressColor: {
    color: theme.palette.primary.main
  },
  successCircularProgressColor: {
    color: theme.palette.success.main
  },
  errorCircularProgressColor: {
    color: theme.palette.error.main
  },
  infoCircularProgressColor: {
    color: theme.palette.info.main
  },
  wrapper: {
    maxWidth: "max-content",
    position: "relative",
    marginRight: theme.spacing(1),
    "&:last-child": {
      marginRight: 0
    }
  },
  wrapperFullWidth: {
    maxWidth: "initial",
    width: "100%"
  },
  buttonFullWidth: {
    width: "100%"
  },
  assignButton: {
    height: theme.spacing(5)
  }
}));

export default useStyles;
