import React from "react";
import FormControl from "@mui/material/FormControl";
import FormControlLabel from "@mui/material/FormControlLabel";
import FormHelperText from "@mui/material/FormHelperText";
import Radio from "@mui/material/Radio";
import RadioGroup from "@mui/material/RadioGroup";
import Skeleton from "@mui/material/Skeleton";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import StyledFormLabel from "components/StyledFormLabel";
import useStyles from "./RadioGroupField.styles";

const RadioGroupField = ({
  radioGroupProps,
  radioButtons,
  labelMessageId,
  fullWidth = false,
  required = false,
  error = false,
  helperText
}) => {
  const { classes, cx } = useStyles();

  return (
    <FormControl fullWidth={fullWidth}>
      {labelMessageId && (
        <StyledFormLabel required={required}>
          <FormattedMessage id={labelMessageId} />
        </StyledFormLabel>
      )}
      <>
        <RadioGroup className={classes.radioGroup} {...radioGroupProps}>
          {radioButtons.map(({ value, dataTestId, disabled = false, label, isLoading = false, size = "small" }) => {
            const radioControl = (
              <FormControlLabel
                key={value}
                disabled={disabled}
                value={value}
                control={<Radio data-test-id={dataTestId} size={size} />}
                label={label}
              />
            );
            return isLoading ? (
              <Skeleton className={cx(fullWidth ? classes.fullWidthSkeleton : "")} key={value}>
                {radioControl}
              </Skeleton>
            ) : (
              radioControl
            );
          })}
        </RadioGroup>
        {error && (
          <FormHelperText variant="outlined" error>
            {helperText}
          </FormHelperText>
        )}
      </>
    </FormControl>
  );
};

RadioGroupField.propTypes = {
  radioButtons: PropTypes.arrayOf(
    PropTypes.shape({
      value: PropTypes.string.isRequired,
      label: PropTypes.node.isRequired,
      disabled: PropTypes.bool,
      isLoading: PropTypes.bool,
      size: PropTypes.string
    })
  ).isRequired,
  labelMessageId: PropTypes.string,
  radioGroupProps: PropTypes.object,
  fullWidth: PropTypes.bool,
  error: PropTypes.bool,
  helperText: PropTypes.string,
  required: PropTypes.bool,
  size: PropTypes.string
};

export default RadioGroupField;
