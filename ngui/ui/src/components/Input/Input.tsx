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
    variant,
    sx,
    ...rest
  } = props;

  const { classes, cx } = useStyles();
  const inputClassName = cx(isMasked ? classes.masked : "");

  const { readOnly = false, style: originalStyles } = InputProps;

  // text-security docs: Use -webkit-text-security if the browser supports it
  // added here due to tss react does not parse kebab-style props properly
  const style = { ...originalStyles, ...(isMasked ? { WebkitTextSecurity: "disc" } : {}) };

  // Please note, disableUnderline not supported by outlined variant.
  // But now we replacing variant to standart if control is readOnly
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
      {...rest}
      inputRef={ref}
    />
  );
});

export default Input;
