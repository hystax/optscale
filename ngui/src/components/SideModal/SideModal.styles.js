import { makeStyles } from "tss-react/mui";

const useStyles = makeStyles()((theme) => ({
  sideModal: {
    width: "40%",
    [theme.breakpoints.down("md")]: {
      width: "60%"
    },
    [theme.breakpoints.down("sm")]: {
      width: "80%"
    }
  }
}));

export default useStyles;
