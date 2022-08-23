import { makeStyles } from "tss-react/mui";

const useStyles = makeStyles()((theme) => ({
  root: {
    width: "100%",
    "& > *": {
      marginTop: theme.spacing(4)
    }
  }
}));

export default useStyles;
