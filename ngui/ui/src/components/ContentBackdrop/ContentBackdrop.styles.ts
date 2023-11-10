import { makeStyles } from "tss-react/mui";

const useStyles = makeStyles()((theme, { bannerMaxWidth = "450px" }) => ({
  root: {
    position: "absolute",
    display: "flex",
    maxWidth: bannerMaxWidth,
    width: "calc(100% - 20px)",
    alignItems: "center",
    flexDirection: "column",
    top: "50%",
    left: "50%",
    zIndex: theme.zIndex.drawer,
    transform: "translate(-50%, -50%)",
    padding: theme.spacing(2)
  },
  icon: {
    width: "4rem",
    height: "4rem",
    marginTop: `calc(-2rem - ${theme.spacing(2)})`,
    marginBottom: theme.spacing(1)
  }
}));

export default useStyles;
