import { forwardRef } from "react";
import MuiCheckbox, { CheckboxProps as MuiCheckboxProps } from "@mui/material/Checkbox";

type CheckboxProps = {
  cssColor?: string;
} & MuiCheckboxProps;

const Checkbox = forwardRef<HTMLButtonElement, CheckboxProps>(({ cssColor, ...rest }, ref) => {
  const sx = cssColor
    ? {
        color: cssColor,
        "&.Mui-checked": {
          color: cssColor,
        },
      }
    : undefined;

  return <MuiCheckbox ref={ref} sx={sx} {...rest} />;
});

export default Checkbox;
