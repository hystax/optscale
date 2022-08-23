import { makeStyles } from "tss-react/mui";

const useStyles = makeStyles()(() => ({
  dashed: {
    display: "inline",
    borderBottom: "1px dashed",
    width: "fit-content"
  },
  cursorPointer: {
    "&:hover": {
      cursor: "pointer"
    }
  },
  right: {
    marginRight: "0.2rem"
  }
}));

export default useStyles;
