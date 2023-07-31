import { makeStyles } from "tss-react/mui";

const useStyles = makeStyles()(() => ({
  button: {
    textTransform: "none"
  },
  dashed: {
    border: "1px dashed"
  },
  uppercase: {
    textTransform: "uppercase"
  },
  link: {
    textDecoration: "none",
    "&:hover": {
      textDecoration: "none"
    }
  },
  tooltipSpan: {
    display: "block" // Required for disabled items in Safari (https://mui.com/components/tooltips/#disabled-elements).
  }
}));

export default useStyles;
