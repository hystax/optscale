import { makeStyles } from "tss-react/mui";

const useStyles = makeStyles()((theme) => ({
  sideModal: {
    height: "100%",
    overflow: "auto",
    width: "40vw",
    [theme.breakpoints.down("md")]: {
      width: "60vw"
    },
    [theme.breakpoints.down("sm")]: {
      width: "80vw"
    },
    transition: "width 0.1s ease-out"
  },
  sideModalExpanded: {
    width: "80vw",
    [theme.breakpoints.down("md")]: {
      width: "85vw"
    },
    [theme.breakpoints.down("sm")]: {
      width: "90vw"
    }
  }
}));

export default useStyles;
