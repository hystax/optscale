import { makeStyles } from "tss-react/mui";

const useStyles = makeStyles()((theme) => ({
  root: {
    height: 230,
    transition: theme.transitions.create("height", {
      duration: theme.transitions.duration.shortest
    })
  },
  fullHeight: {
    height: "100%"
  },
  title: {
    justifyContent: "center"
  },
  titleContainer: {
    textAlign: "center"
  },
  descriptionContainer: {
    wordBreak: "break-word"
  },
  illustrationContainer: {
    display: "flex",
    justifyContent: "center"
  },
  illustration: {
    maxWidth: "120px",
    marginTop: "-60px",
    transition: theme.transitions.create("filter", {
      easing: theme.transitions.easing.sharp,
      duration: theme.transitions.duration.standard
    })
  },
  blackAndWhite: {
    filter: "grayscale(1)"
  },
  subtitle: {
    display: "inline",
    borderBottom: "1px dashed",
    width: "fit-content",
    "&:hover": {
      cursor: "pointer"
    }
  }
}));

export default useStyles;
