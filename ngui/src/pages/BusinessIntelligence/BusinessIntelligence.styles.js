import { makeStyles } from "tss-react/mui";
import { SPACING_4 } from "utils/layouts";

const useStyles = makeStyles()((theme) => ({
  centered: {
    marginLeft: "auto",
    marginRight: "auto",
    display: "block",
    textAlign: "center"
  },
  content: {
    maxWidth: "500px",
    display: "flex",
    alignItems: "center",
    flexDirection: "column",
    "&>div": {
      marginBottom: theme.spacing(SPACING_4)
    }
  }
}));

export default useStyles;
