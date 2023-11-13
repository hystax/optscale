import { makeStyles } from "tss-react/mui";

const useStyles = makeStyles()((theme) => ({
  wrapper: {
    display: "flex",
    flexGrow: 1,
    "& .Mui-selected": {
      background: theme.palette.secondary.main,
      color: theme.palette.secondary.contrastText,
      "&:hover": {
        backgroundColor: theme.palette.secondary.light
      }
    }
  },
  right: {
    justifyContent: "flex-end"
  },
  center: {
    justifyContent: "center"
  },
  left: {
    justifyContent: "flex-start"
  }
}));

export default useStyles;
