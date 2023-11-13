import { makeStyles } from "tss-react/mui";

const useStyles = makeStyles()((theme) => ({
  label: {
    paddingLeft: theme.spacing(1.75),
    marginBottom: theme.spacing(0.25),
    fontSize: "0.75rem"
  }
}));

export default useStyles;
