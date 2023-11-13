import { makeStyles } from "tss-react/mui";

const useStyles = makeStyles()((theme) => ({
  wrapper: {
    width: theme.spacing(40),
    [theme.breakpoints.up("sm")]: {
      width: theme.spacing(64)
    }
  },
  customContainer: {
    textAlign: "center"
  },
  customTypography: {
    fontWeight: "bold",
    fontSize: "1rem"
  },
  listContainer: {
    paddingBottom: 0,
    paddingTop: 0
  },
  buttonLink: {
    "&:hover": {
      textDecoration: "none"
    },
    color: "black"
  }
}));

export default useStyles;
