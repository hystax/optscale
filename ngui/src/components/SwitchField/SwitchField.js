import React from "react";
import FormControl from "@mui/material/FormControl";
import FormControlLabel from "@mui/material/FormControlLabel";
import Switch from "@mui/material/Switch";
import Typography from "@mui/material/Typography";
import PropTypes from "prop-types";
import { Controller } from "react-hook-form";
import { FormattedMessage } from "react-intl";
import useStyles from "./SwitchField.styles";

const SwitchField = ({ name, labelMessageId, control, endAdornment = null, defaultValue = false, dataTestIds = {} }) => {
  const { classes, cx } = useStyles();
  return (
    <FormControl fullWidth className={cx(classes.formControl, endAdornment ? classes.formControlAdornedEnd : "")}>
      <FormControlLabel
        control={
          <Controller
            name={name}
            control={control}
            defaultValue={defaultValue}
            render={({ field: { onChange, value } }) => (
              <Switch
                checked={value}
                onChange={(e) => onChange(e.target.checked)}
                inputProps={{ "data-test-id": dataTestIds.input }}
              />
            )}
          />
        }
        label={
          <Typography data-test-id={dataTestIds.labelText}>
            <FormattedMessage id={labelMessageId} />
          </Typography>
        }
        className={endAdornment ? classes.labelAdornedEnd : ""}
      />
      {endAdornment}
    </FormControl>
  );
};

SwitchField.propTypes = {
  name: PropTypes.string.isRequired,
  control: PropTypes.object.isRequired,
  labelMessageId: PropTypes.string.isRequired,
  endAdornment: PropTypes.node,
  defaultValue: PropTypes.bool,
  dataTestIds: PropTypes.shape({
    labelText: PropTypes.string,
    input: PropTypes.string
  })
};

export default SwitchField;
