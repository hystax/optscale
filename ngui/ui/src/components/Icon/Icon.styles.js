import { makeStyles } from "tss-react/mui";

const useStyles = makeStyles()((theme) => ({
  icon: {
    verticalAlign: "middle"
  },
  info: {
    color: theme.palette.info.main
  },
  primary: {
    color: theme.palette.primary.main
  },
  warning: {
    color: theme.palette.warning.main
  },
  error: {
    color: theme.palette.error.main
  },
  success: {
    color: theme.palette.success.main
  },
  white: {
    color: theme.palette.common.white
  },
  inherit: {
    color: "inherit"
  },
  right: {
    marginRight: "0.2rem"
  },
  left: {
    marginLeft: "0.2rem"
  }
}));

export default useStyles;
