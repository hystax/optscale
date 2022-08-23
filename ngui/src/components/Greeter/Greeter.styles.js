import { makeStyles } from "tss-react/mui";

const getFormAndMapWrapperClasses = (theme) => {
  const wrapperClass = {
    [theme.breakpoints.down("xl")]: {
      width: 450
    },
    [theme.breakpoints.down("sm")]: {
      maxWidth: 450,
      width: "100%"
    },
    width: 600
  };
  return {
    wrapper: wrapperClass
  };
};

const useStyles = makeStyles()((theme) => ({
  root: {
    height: "100vh"
  },
  centeredFlexColumnDirection: {
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    flexDirection: "column",
    textAlign: "center"
  },
  linkWrapper: {
    width: "100%",
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    [theme.breakpoints.down("md")]: {
      justifyContent: "space-around"
    }
  },
  imagesWithCaptions: {
    maxWidth: "590px",
    [theme.breakpoints.down("md")]: {
      justifyContent: "center"
    },
    [theme.breakpoints.up("xl")]: {
      maxWidth: "690px"
    }
  },
  rightTextColor: {
    color: theme.palette.common.white
  },
  imageWithCaptionWrapper: {
    alignItems: "center",
    display: "flex",
    flexDirection: "column",
    width: "100%"
  },
  image: {
    width: "80%",
    marginBottom: theme.spacing(1),
    [theme.breakpoints.down("md")]: {
      width: "50%"
    }
  },
  caption: {
    textAlign: "center"
  },
  icon: {
    verticalAlign: "bottom",
    marginRight: "0.5rem"
  },
  leftSideGrid: {
    backgroundColor: theme.palette.common.white
  },
  rightSideGrid: {
    backgroundColor: theme.palette.info.dark
  },
  ...getFormAndMapWrapperClasses(theme)
}));

export default useStyles;
