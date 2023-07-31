import { makeStyles } from "tss-react/mui";

const useStyles = makeStyles()((theme) => ({
  icon: {
    fontSize: "4rem",
    color: theme.palette.error.main
  }
}));

export default useStyles;
