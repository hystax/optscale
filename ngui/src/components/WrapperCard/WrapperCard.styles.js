import { makeStyles } from "tss-react/mui";

const useStyles = makeStyles()((theme) => ({
  spacer: {
    flexGrow: 1
  },
  actions: {
    borderTop: "1px solid lightGrey",
    height: "2.5rem"
  },
  content: {
    paddingTop: theme.spacing(1)
  },
  card: {
    paddingTop: theme.spacing(2),
    paddingBottom: theme.spacing(2)
  },
  buttonLink: {
    "&:hover": {
      textDecoration: "none"
    }
  },
  halfWidth: {
    [theme.breakpoints.up("md")]: {
      width: "50%"
    }
  },
  quarterWidth: {
    [theme.breakpoints.up("md")]: {
      width: "25%"
    }
  },
  mainCard: {
    overflow: "visible"
  },
  alignedWrapper: {
    height: "100%"
  }
}));

export default useStyles;
