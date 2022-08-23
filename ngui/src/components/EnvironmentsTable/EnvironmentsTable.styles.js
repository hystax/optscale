import { makeStyles } from "tss-react/mui";

const useStyles = makeStyles()((theme) => ({
  marginBottom: {
    "& > *": {
      marginBottom: theme.spacing(1),
      "&:last-child": {
        marginBottom: 0
      }
    }
  }
}));

export default useStyles;
