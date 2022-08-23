import { makeStyles } from "tss-react/mui";

const useStyles = makeStyles()(() => ({
  formControl: {
    flexDirection: "row",
    alignItems: "center"
  },
  labelAdornedEnd: {
    marginRight: 0
  },
  formControlAdornedEnd: {
    paddingRight: 14
  }
}));

export default useStyles;
