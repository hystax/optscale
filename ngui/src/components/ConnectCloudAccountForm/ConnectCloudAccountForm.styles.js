import { makeStyles } from "tss-react/mui";

const useStyles = makeStyles()((theme) => ({
  tile: {
    borderColor: theme.palette.secondary.main,
    borderWidth: `2px`
  },
  inactiveTile: {
    filter: "grayscale(1)",
    borderWidth: `1px`,
    "&:hover": {
      borderColor: theme.palette.info.main,
      filter: "grayscale(0)"
    }
  }
}));

export default useStyles;
