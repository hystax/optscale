import { forwardRef } from "react";
import MuiCheckbox from "@mui/material/Checkbox";

const Checkbox = forwardRef(({ cssColor, ...rest }, ref) => {
  const sx = cssColor
    ? {
        color: cssColor,
        "&.Mui-checked": {
          color: cssColor
        }
      }
    : undefined;

  return <MuiCheckbox ref={ref} sx={sx} {...rest} />;
});

export default Checkbox;
