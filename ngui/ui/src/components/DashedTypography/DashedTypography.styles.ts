import { makeStyles } from "tss-react/mui";

const useStyles = makeStyles()(() => ({
  dashed: {
    display: "inline",
    position: "relative",
    width: "fit-content",
    "&:after": {
      content: '""',
      position: "absolute",
      bottom: -1,
      left: 0,
      width: "100%",
      borderBottom: "1px dashed",
    },
  },
  cursorPointer: {
    "&:hover": {
      cursor: "pointer",
    },
  },
  right: {
    marginRight: "0.2rem",
  },
}));

export default useStyles;
