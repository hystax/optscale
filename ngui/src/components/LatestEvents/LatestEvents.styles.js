import { alpha } from "@mui/material/styles";

import { makeStyles } from "tss-react/mui";

const useStyles = makeStyles()((theme) => ({
  button: {
    [theme.breakpoints.up("md")]: {
      color: theme.palette.primary.contrastText,
      "&:hover": {
        backgroundColor: alpha(theme.palette.primary.contrastText, 0.2)
      }
    }
  }
}));

export default useStyles;
