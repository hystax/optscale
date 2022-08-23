import { makeStyles } from "tss-react/mui";

const useStyles = makeStyles()((theme) => ({
  alert: {
    backgroundColor: theme.palette.secondary.main,
    color: theme.palette.secondary.contrastText,
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
  success: {
    backgroundColor: theme.palette.success.main,
    color: theme.palette.common.white
  }
}));

export default useStyles;
