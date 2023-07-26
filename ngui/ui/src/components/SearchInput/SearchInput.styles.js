import { alpha } from "@mui/material/styles";

import { makeStyles } from "tss-react/mui";

const useStyles = makeStyles()((theme) => ({
  input: {
    width: "15rem",
    "&:focus-within": {
      width: "20rem"
    },
    transition: theme.transitions.create("width")
  },
  clearSearchIcon: {
    color: alpha(theme.palette.text.primary, 0.26)
  }
}));

export default useStyles;
