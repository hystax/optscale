import { MenuItem } from "@mui/material";
import { withStyles } from "tss-react/mui";

/**
 * Please consider implementation details of Select if you decide to write a custom MenuItem component
 * - https://stackoverflow.com/questions/68378474/mui-select-custom-menuitem-not-working-properly
 * - https://stackoverflow.com/questions/66943324/mui-select-component-with-custom-children-item
 */
const Item = withStyles(MenuItem, (theme) => ({
  root: {
    paddingLeft: theme.spacing(4)
  }
}));

export default Item;
