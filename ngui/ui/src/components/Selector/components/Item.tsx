import { MenuItem, MenuItemProps } from "@mui/material";
import { SPACING_2 } from "utils/layouts";

type ItemProps = MenuItemProps & {
  depth?: number;
};

const PADDING_SPACING = SPACING_2;

/**
 * Please consider implementation details of Select if you decide to customize this component
 * - https://stackoverflow.com/questions/68378474/mui-select-custom-menuitem-not-working-properly
 * - https://stackoverflow.com/questions/66943324/mui-select-component-with-custom-children-item
 */
const Item = (props: ItemProps) => {
  const { depth = 0, ...rest } = props;

  return (
    <MenuItem
      {...rest}
      sx={{
        ...rest.sx,
        paddingLeft: (theme) => {
          if (depth) {
            return theme.spacing(PADDING_SPACING + depth * PADDING_SPACING);
          }
          return theme.spacing(PADDING_SPACING);
        }
      }}
    />
  );
};

export default Item;
