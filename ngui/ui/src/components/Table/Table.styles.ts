import { makeStyles } from "tss-react/mui";

const useStyles = makeStyles()(() => ({
  tableContainer: {
    width: "100%",
    display: "block",
    wordBreak: "initial" // shown inside MUI Drawer table inherits word-break: "break-word" which leads to letter-by-letter break in side modals, for example
  },
  hoverableRow: {
    cursor: "pointer"
  }
}));

export default useStyles;
