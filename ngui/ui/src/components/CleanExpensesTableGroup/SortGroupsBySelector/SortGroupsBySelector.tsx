import Box from "@mui/material/Box";
import Selector, { Item, ItemContent } from "components/Selector";
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
        id="sort-groups-by-selector"
        variant="standard"
        onChange={(value) => {
          setSortGroupsBy(value);
        }}
        value={sortGroupsBy}
        sx={{
          minWidth: "initial"
        }}
      >
        <Item value={TOTAL_EXPENSES}>
          <ItemContent>{intl.formatMessage({ id: "expenses" }).toLocaleLowerCase()}</ItemContent>
        </Item>
        <Item value={COUNT}>
          <ItemContent>{intl.formatMessage({ id: "resourceCount" }).toLocaleLowerCase()}</ItemContent>
        </Item>
      </Selector>
    </Box>
  );
};

export default SortGroupsBySelector;
