import { makeStyles } from "tss-react/mui";

const useStyles = makeStyles()(() => ({
  readOnly: {
    "&:before": {
      borderColor: "transparent"
    },
    "&:after": {
      borderColor: "transparent"
    },
    "&:hover:not(.Mui-disabled, .Mui-error):before": {
      borderColor: "transparent"
    },
    "&.Mui-focused .MuiSelect-standard": {
      backgroundColor: "initial"
    },
    "&.Mui-error": {
      ":before": {
        borderBottomColor: "transparent"
      },
      ":after": {
        borderBottomColor: "transparent"
      }
    },
    ".MuiSelect-standard": {
      cursor: "text",
      // enable value text selection
      userSelect: "auto"
    }
  },
  adornmentIconPosition: {
    position: "relative"
  },
  menu: {
    maxHeight: "400px"
  }
}));

export default useStyles;
