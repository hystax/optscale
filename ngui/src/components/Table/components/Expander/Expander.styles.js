import { makeStyles } from "tss-react/mui";

const useStyles = makeStyles()((theme) => ({
  expand: {
    transform: "rotate(-90deg)",
    marginLeft: "-10px"
  },
  expandOpen: {
    transform: "rotate(0deg)"
  },
  treePadding: {
    paddingLeft: theme.spacing(3.5)
  }
}));

export default useStyles;
