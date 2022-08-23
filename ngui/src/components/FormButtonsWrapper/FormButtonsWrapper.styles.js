import { makeStyles } from "tss-react/mui";

const useStyles = makeStyles()((theme) => ({
  wrapper: {
    "& > *": {
      marginRight: theme.spacing(1),
      "&:last-child": {
        marginRight: 0
      }
    }
  }
}));

export default useStyles;
