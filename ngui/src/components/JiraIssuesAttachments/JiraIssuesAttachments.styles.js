import { makeStyles } from "tss-react/mui";

const useStyles = makeStyles()((theme) => ({
  list: {
    margin: 0,
    paddingInlineStart: theme.spacing(3)
  },
  toggleListItem: {
    listStyleType: "none"
  }
}));

export default useStyles;
