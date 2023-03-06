import { makeStyles } from "tss-react/mui";

const useStyles = makeStyles()(() => ({
  menuItems: {
    overflow: "auto",
    maxHeight: "350px"
  },
  menuItem: {
    paddingBottom: "0px",
    paddingTop: "0px"
  }
}));

export default useStyles;
