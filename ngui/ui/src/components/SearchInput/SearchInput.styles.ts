import { alpha } from "@mui/material/styles";

import { makeStyles } from "tss-react/mui";

const useStyles = makeStyles()((theme) => ({
  clearSearchIcon: {
    color: alpha(theme.palette.text.primary, 0.26)
  }
}));

export default useStyles;
