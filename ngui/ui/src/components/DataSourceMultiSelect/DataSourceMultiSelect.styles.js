import { makeStyles } from "tss-react/mui";

const useStyles = makeStyles()((theme) => ({
  formControl: {
    minWidth: "250px",
    maxWidth: "100%"
  },
  // overriding theme style — no need for selected items background in this control
  menuItem: {
    "&.Mui-selected": {
      backgroundColor: "unset",
      "&.Mui-focusVisible": { background: "unset" },
      "&:hover": {
        backgroundColor: "unset"
      }
    }
  },
  checkbox: {
    padding: `0 ${theme.spacing(1)} 0 0`
  }
}));

export default useStyles;
