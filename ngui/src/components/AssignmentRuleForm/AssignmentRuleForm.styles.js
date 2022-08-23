import { makeStyles } from "tss-react/mui";
import { SPACING_1 } from "utils/layouts";

const useStyles = makeStyles()((theme) => ({
  item: {
    width: "100%",
    minWidth: 0
  },
  keyValueInput: {
    width: `calc(50% - ${theme.spacing(SPACING_1 / 2)})`
  },
  spaceRight: {
    marginRight: theme.spacing(1)
  },
  deleteButton: {
    alignItems: "flex-end"
  }
}));

export default useStyles;
