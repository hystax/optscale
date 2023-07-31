import React from "react";
import { IconButton, Typography } from "@mui/material";
import PropTypes from "prop-types";
import useStyles from "./Day.styles";

const Day = ({ disabled, highlighted, outlined, filled, onClick, onHover, value }) => {
  const { classes, cx } = useStyles();
  return (
    <div
      className={cx(classes.buttonContainer, {
        [classes.highlighted]: !disabled && highlighted
      })}
    >
      <IconButton
        className={cx(classes.button, {
          [classes.outlined]: !disabled && outlined,
          [classes.filled]: !disabled && filled
        })}
        disabled={disabled}
        onClick={onClick}
        onMouseOver={onHover}
      >
        <Typography
          className={cx(classes.buttonText, {
            [classes.contrast]: !disabled && filled
          })}
          disabled={disabled}
        >
          {value}
        </Typography>
      </IconButton>
    </div>
  );
};

Day.propTypes = {
  value: PropTypes.oneOfType([PropTypes.number, PropTypes.string]).isRequired,
  filled: PropTypes.bool,
  outlined: PropTypes.bool,
  highlighted: PropTypes.bool,
  disabled: PropTypes.bool,
  startOfRange: PropTypes.bool,
  endOfRange: PropTypes.bool,
  onClick: PropTypes.func,
  onHover: PropTypes.func
};

export default Day;
