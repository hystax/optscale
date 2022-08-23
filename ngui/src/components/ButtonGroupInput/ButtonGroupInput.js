import React from "react";
import FormControl from "@mui/material/FormControl";
import Typography from "@mui/material/Typography";
import PropTypes from "prop-types";
import ButtonGroup from "components/ButtonGroup";
import StyledFormLabel from "components/StyledFormLabel";
import useStyles from "./ButtonGroupInput.styles";

const ButtonGroupInput = ({
  labelText,
  buttons,
  activeButtonIndex,
  fullWidth = false,
  required = true,
  helperText,
  typographyProps
}) => {
  const { classes } = useStyles();

  return (
    <FormControl fullWidth={fullWidth}>
      <StyledFormLabel required={required}>{labelText}</StyledFormLabel>
      <ButtonGroup fullWidth={fullWidth} buttons={buttons} activeButtonIndex={activeButtonIndex} />
      {helperText && (
        <Typography className={classes.helperText} {...typographyProps}>
          {helperText}
        </Typography>
      )}
    </FormControl>
  );
};

ButtonGroupInput.propTypes = {
  labelText: PropTypes.node.isRequired,
  buttons: PropTypes.array.isRequired,
  activeButtonIndex: PropTypes.number.isRequired,
  helperText: PropTypes.node,
  fullWidth: PropTypes.bool,
  required: PropTypes.bool,
  typographyProps: PropTypes.object
};

export default ButtonGroupInput;
