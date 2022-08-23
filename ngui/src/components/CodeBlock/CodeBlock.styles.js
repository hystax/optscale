import { makeStyles } from "tss-react/mui";

const useStyles = makeStyles()((theme) => ({
  wrapper: {
    backgroundColor: theme.palette.background.default,
    borderRadius: theme.spacing(0.5),
    padding: theme.spacing(2),
    display: "flex",
    alignItems: "flex-start",
    justifyContent: "space-between"
  },
  codeBlock: {
    margin: 0,
    width: "100%",
    overflow: "auto"
  }
}));

export default useStyles;
