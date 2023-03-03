import { makeStyles } from "tss-react/mui";

const useStyles = makeStyles()((theme) => ({
  alert: {
    borderRadius: 0,
    paddingTop: 0,
    paddingBottom: 0,
    "& .MuiAlert-message": {
      width: "100%",
      display: "flex",
      justifyContent: "center",
      alignItems: "center"
    }
  },
  secondary: {
    backgroundColor: theme.palette.secondary.main,
    color: theme.palette.secondary.contrastText,
    ".close-alert-button": {
      color: theme.palette.secondary.contrastText
    }
  },
  success: {
    backgroundColor: theme.palette.success.main,
    color: theme.palette.common.white,
    ".close-alert-button": {
      color: theme.palette.common.white
    }
  },
  info: {
    backgroundColor: theme.palette.info.main,
    color: theme.palette.common.white,
    ".close-alert-button": {
      color: theme.palette.common.white
    }
  }
}));

export default useStyles;
