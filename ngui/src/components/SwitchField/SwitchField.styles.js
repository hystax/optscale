import { makeStyles } from "tss-react/mui";

const useStyles = makeStyles()(() => ({
  formControl: {
    display: "flex",
    flexDirection: "row",
    alignItems: "center"
  },
  labelAdornedEnd: {
    marginRight: 0
  }
}));

export default useStyles;
