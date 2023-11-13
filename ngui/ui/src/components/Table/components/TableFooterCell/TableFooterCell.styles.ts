import { makeStyles } from "tss-react/mui";

const useStyles = makeStyles()((theme) => ({
  cell: {
    color: theme.palette.text.primary,
    borderBottom: "none"
  }
}));

export default useStyles;
