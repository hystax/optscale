import { makeStyles } from "tss-react/mui";

const useStyles = makeStyles()(() => ({
  chip: {
    maxWidth: "100%"
  },
  uppercase: {
    textTransform: "uppercase"
  },
  // https://mui.com/material-ui/react-chip/#multiline-chip
  multiline: {
    height: "auto",
    "& .MuiChip-label": {
      display: "block",
      whiteSpace: "normal"
    }
  }
}));

export default useStyles;
