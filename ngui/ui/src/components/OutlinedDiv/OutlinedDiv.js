import React, { forwardRef } from "react";
import TextField from "@mui/material/TextField";
import PropTypes from "prop-types";

const InputComponent = forwardRef(({ inputRef, ...other }, ref) => <div ref={ref} {...other} />);

const OutlinedDiv = ({ children, label, endAdornment, dataTestId, margin = "none", ...rest }) => (
  <TextField
    variant="outlined"
    label={label ? <span style={{ whiteSpace: "nowrap" }}>{label}</span> : undefined}
    InputLabelProps={{ shrink: true }}
    InputProps={{
      inputComponent: InputComponent,
      endAdornment,
      "data-test-id": dataTestId
    }}
    inputProps={{ children }}
    margin={margin}
    {...rest}
  />
);

OutlinedDiv.propTypes = {
  children: PropTypes.node,
  label: PropTypes.node,
  endAdornment: PropTypes.node,
  dataTestId: PropTypes.string,
  margin: PropTypes.string
};

export default OutlinedDiv;
