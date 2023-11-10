import { makeStyles } from "tss-react/mui";

const useStyles = makeStyles()((theme) => ({
  sectionDesktop: {
    display: "none",
    [theme.breakpoints.up("md")]: {
      display: "flex",
      alignItems: "center"
    }
  },
  sectionMobile: {
    display: "flex",
    [theme.breakpoints.up("md")]: {
      display: "none"
    }
  },
  customMenuItem: {
    display: "flex",
    alignItems: "center",
    flexDirection: "column"
  }
}));

export default useStyles;
