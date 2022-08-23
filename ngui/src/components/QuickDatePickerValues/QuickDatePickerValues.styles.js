import { makeStyles } from "tss-react/mui";

const useStyles = makeStyles()((theme) => ({
  container: {
    width: "max-content",
    display: "flex",
    "& > *": {
      marginRight: theme.spacing(1),
      "&:last-child": {
        marginRight: 0
      }
    }
  }
}));

export default useStyles;
