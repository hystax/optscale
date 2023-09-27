import { makeStyles } from "tss-react/mui";

const useStyles = makeStyles()((theme) => ({
  title: {
    color: theme.palette.common.white
  },
  logosWrapper: {
    width: "100%",
    display: "flex",
    flexWrap: "wrap",
    rowGap: "10px",
    columnGap: "45px",
    justifyContent: "center"
  },
  logoWrapper: {
    width: 25,
    height: 54,
    display: "flex"
  },
  logoImage: {
    width: "100%"
  }
}));

export default useStyles;
