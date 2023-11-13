import { makeStyles } from "tss-react/mui";

const useStyles = makeStyles()((theme) => ({
  customSelectorStyles: {
    minWidth: theme.spacing(4),
    marginRight: 0
  }
}));

export default useStyles;
