import { makeStyles } from "tss-react/mui";
import { SPACING_1 } from "utils/layouts";

const useStyles = makeStyles()((theme) => ({
  actionBar: {
    display: "flex",
    justifyContent: "space-between",
    gap: theme.spacing(SPACING_1)
  },
  actionBarPart: {
    display: "flex",
    alignItems: "center",
    gap: theme.spacing(SPACING_1)
  },
  cardsGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fill, minmax(340px, 1fr))",
    gap: theme.spacing(SPACING_1),
    marginTop: theme.spacing(SPACING_1)
  }
}));

export default useStyles;
