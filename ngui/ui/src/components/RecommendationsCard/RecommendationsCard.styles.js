import { makeStyles } from "tss-react/mui";

const useStyles = makeStyles()((theme) => ({
  infoCard: {
    height: "120px",
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "center",
    padding: theme.spacing(2)
  }
}));

export default useStyles;
