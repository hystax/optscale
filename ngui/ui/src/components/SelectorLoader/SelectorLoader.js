import React from "react";
import ArrowDropDownIcon from "@mui/icons-material/ArrowDropDown";
import FormControl from "@mui/material/FormControl";
import FormHelperText from "@mui/material/FormHelperText";
import InputLabel from "@mui/material/InputLabel";
import MenuItem from "@mui/material/MenuItem";
import Select from "@mui/material/Select";
import Skeleton from "@mui/material/Skeleton";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import useStyles from "./SelectorLoader.styles";

const SelectorLoader = ({ labelId, customClass, readOnly = false, isRequired = false, error, helperText, fullWidth }) => {
  const { classes, cx } = useStyles();

  // TODO -  we need a generic detection of a mobile mode, passing props for this is not stable.
  const formControlClasses = cx(classes.selector, customClass || "");

  const label = <FormattedMessage id={labelId} />;

  return (
    <FormControl fullWidth={fullWidth} variant="outlined" className={formControlClasses} error={error}>
      <InputLabel required={isRequired}>{label}</InputLabel>
      <Select label={label} readOnly={readOnly} IconComponent={readOnly ? () => null : ArrowDropDownIcon} value={" "}>
        <MenuItem value={" "}>
          <Skeleton />
        </MenuItem>
      </Select>
      {helperText ? <FormHelperText>{helperText}</FormHelperText> : null}
    </FormControl>
  );
};

SelectorLoader.propTypes = {
  labelId: PropTypes.string.isRequired,
  isRequired: PropTypes.bool,
  customClass: PropTypes.string,
  error: PropTypes.bool,
  helperText: PropTypes.string,
  fullWidth: PropTypes.bool,
  readOnly: PropTypes.bool
};

export default SelectorLoader;
