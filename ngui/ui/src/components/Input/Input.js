import React, { forwardRef } from "react";
import TextField from "@mui/material/TextField";
import PropTypes from "prop-types";
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

  const { readOnly = false } = InputProps;
  // Please note, disableUnderline not supported by outlined variant.
  // But now we replacing variant to standart if control is readOnly
  const InputPropsMerged = readOnly ? { ...InputProps, disableUnderline: true } : InputProps;

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

Input.propTypes = {
  fullWidth: PropTypes.bool,
  variant: PropTypes.oneOf(["standard", "outlined", "filled"]),
  type: PropTypes.string,
  inputProps: PropTypes.object,
  InputProps: PropTypes.object,
  InputLabelProps: PropTypes.object,
  isMasked: PropTypes.bool,
  dataTestId: PropTypes.string,
  sx: PropTypes.object
};

export default Input;
