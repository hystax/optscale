import { makeStyles } from "tss-react/mui";

const useStyles = makeStyles()(() => ({
  horizontalScroll: {
    width: "100%",
    overflowX: "auto",
    display: "block",
    wordBreak: "initial" // shown inside MUI Drawer table inherits word-break: "break-word" which leads to letter-by-letter break in side modals, for example
  }
}));

export default useStyles;
