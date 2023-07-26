import { makeStyles } from "tss-react/mui";

const useStyles = makeStyles()((theme) => ({
  noEnvironmentsWrapper: { display: "flex", flexDirection: "column", alignItems: "center" },
  icon: {
    width: "4rem",
    height: "4rem",
    marginBottom: theme.spacing(2)
  }
}));

export default useStyles;
