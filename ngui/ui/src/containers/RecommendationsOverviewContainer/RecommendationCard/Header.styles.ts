import { makeStyles } from "tss-react/mui";
import { SPACING_2 } from "utils/layouts";

const useStyles = makeStyles()((theme) => ({
  header: {
    display: "flex",
    flexDirection: "row",
    marginBottom: theme.spacing(SPACING_2),
    justifyContent: "space-between",
    ":only-child": {
      marginBottom: 0
    }
  },
  titleText: {
    display: "flex"
  },
  value: {
    display: "flex",
    flexDirection: "column",
    alignItems: "flex-end"
  },
  title: {
    marginRight: theme.spacing(SPACING_2)
  }
}));

export default useStyles;
