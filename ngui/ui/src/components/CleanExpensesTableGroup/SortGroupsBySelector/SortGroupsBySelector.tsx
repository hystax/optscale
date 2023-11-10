import Box from "@mui/material/Box";
import Selector from "components/Selector";
import { intl } from "translations/react-intl-config";
import { TOTAL_EXPENSES, COUNT } from "../constant";
import useStyles from "./SortGroupsBySelector.styles";

export const SORT_GROUPS_BY = [
  {
    name: intl.formatMessage({ id: "expenses" }).toLowerCase(),
    value: TOTAL_EXPENSES
  },
  {
    name: intl.formatMessage({ id: "resourceCount" }).toLowerCase(),
    value: COUNT
  }
];

const SortGroupsBySelector = ({ sortGroupsBy, setSortGroupsBy }) => {
  const { classes } = useStyles();

  return (
    <Box className={classes.sortGroupsByWrapper} display="flex" alignItems="center">
      <span className={classes.titleText}>{intl.formatMessage({ id: "sortGroupsBy" })}</span>
      <Selector
        data={{
          selected: sortGroupsBy,
          items: SORT_GROUPS_BY
        }}
        variant="standard"
        dataTestId="select_sort_groups_by"
        onChange={(value) => {
          setSortGroupsBy(value);
        }}
        customClass={classes.selector}
      />
    </Box>
  );
};

export default SortGroupsBySelector;
