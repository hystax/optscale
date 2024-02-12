import { forwardRef } from "react";
import TextField from "@mui/material/TextField";

import useStyles from "./Input.styles";

// TODO - pass inputProps and InputLabelProps correctly not to override the defaults,
// Investigate the difference between inputProps and InputProps
const Input = forwardRef((props, ref) => {
  const {
    dataTestId,
    fullWidth = true,
    type = "text",
    inputProps = {},
    InputProps = {},
    InputLabelProps = {},
    isMasked = false,
    minRows,
    maxRows,
    variant,
    sx,
    ...rest
  } = props;

  const { classes, cx } = useStyles();

  const inputClassName = cx(isMasked ? classes.masked : "");

  const { readOnly = false, style } = InputProps;

  // Please note, disableUnderline not supported by outlined variant.
  // But now we replacing variant to standard if control is readOnly
  const InputPropsMerged = { ...InputProps, style, ...(readOnly ? { disableUnderline: true } : {}) };

  return (
    <TextField
      variant={readOnly ? "standard" : variant}
      fullWidth={fullWidth}
      type={type}
      onCopy={isMasked ? (event) => event.preventDefault() : undefined}
      inputProps={{
        ...inputProps,
        "data-test-id": dataTestId,
        className: cx(inputClassName, inputProps.className)
      }}
      sx={sx}
      InputLabelProps={{
        shrink: true,
        ...InputLabelProps
      }}
      InputProps={InputPropsMerged}
      minRows={minRows}
      maxRows={maxRows}
      {...rest}
      inputRef={ref}
    />
  );
});

export default Input;
