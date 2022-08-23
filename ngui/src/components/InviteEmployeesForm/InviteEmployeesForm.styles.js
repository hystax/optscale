import { makeStyles } from "tss-react/mui";

const useStyles = makeStyles()(() => ({
  item: {
    width: "100%",
    minWidth: 0
  },
  deleteButton: {
    alignItems: "flex-end"
  }
}));

export default useStyles;
