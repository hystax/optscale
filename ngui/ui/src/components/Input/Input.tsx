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
    onBlur,
    onChange,
    ...rest
  } = props;

  const { classes, cx } = useStyles();

  const inputClassName = cx(isMasked ? classes.masked : "");

  const { readOnly } = InputProps;

  // Sensitive values (passwords, masked secrets) are sent verbatim - trimming them could silently
  // corrupt a real value, so leading/trailing whitespace is only cleaned up for regular text fields.
  const isTrimmable = type !== "password" && !isMasked;

  const handleBlur = (event) => {
    const { target } = event;
    if (isTrimmable && typeof target.value === "string") {
      const trimmedValue = target.value.trim();
      if (trimmedValue !== target.value) {
        target.value = trimmedValue;
        onChange?.(event);
      }
    }
    onBlur?.(event);
  };

  return (
    <TextField
      variant={readOnly ? "outlined" : variant}
      fullWidth={fullWidth}
      type={type}
      onCopy={isMasked ? (event) => event.preventDefault() : undefined}
      inputProps={{
        ...inputProps,
        "data-test-id": dataTestId,
        className: cx(inputClassName, inputProps.className),
      }}
      sx={{
        sx,
        fieldset: {
          ...sx?.fieldset,
          border: readOnly ? "none" : undefined,
        },
      }}
      InputLabelProps={{
        shrink: true,
        ...InputLabelProps,
      }}
      InputProps={InputProps}
      minRows={minRows}
      maxRows={maxRows}
      onChange={onChange}
      onBlur={handleBlur}
      {...rest}
      inputRef={ref}
    />
  );
});

export default Input;
