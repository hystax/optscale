import MuiCheckbox from "@mui/material/Checkbox";

const Checkbox = ({ cssColor, ...rest }) => {
  const sx = cssColor
    ? {
        color: cssColor,
        "&.Mui-checked": {
          color: cssColor
        }
      }
    : undefined;

  return <MuiCheckbox sx={sx} {...rest} />;
};

export default Checkbox;
