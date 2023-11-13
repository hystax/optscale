import { alpha } from "@mui/material/styles";
import { makeStyles } from "tss-react/mui";

const useStyles = makeStyles()((theme) => ({
  content: {
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    flexWrap: "wrap"
  },
  dropzone: {
    minHeight: "200px",
    height: "100%",
    width: "100%",
    border: `1px ${theme.palette.primary.main} dashed`,
    cursor: "pointer",
    flexDirection: "column"
  },
  error: {
    borderColor: theme.palette.error.main
  },
  highlight: {
    backgroundColor: alpha(theme.palette.primary.main, 0.04)
  }
}));

export default useStyles;
