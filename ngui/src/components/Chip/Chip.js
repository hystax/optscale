import React from "react";
import CancelIcon from "@mui/icons-material/Cancel";
import MuiChip from "@mui/material/Chip";
import PropTypes from "prop-types";
import useStyles from "./Chip.styles";

const Chip = ({ color = "info", variant = "filled", size = "small", uppercase = false, dataTestIds = {}, ...rest }) => {
  const { classes, cx } = useStyles();

  const chipClasses = cx(classes.chip, uppercase ? classes.uppercase : "");

  const { chip: chipDataTestId, deleteIcon: deleteIconDataTestId } = dataTestIds;

  return (
    <MuiChip
      {...rest}
      variant={variant}
      color={color}
      deleteIcon={<CancelIcon data-test-id={deleteIconDataTestId} />}
      data-test-id={chipDataTestId}
      className={chipClasses}
      size={size}
    />
  );
};

Chip.propTypes = {
  color: PropTypes.string,
  variant: PropTypes.string,
  size: PropTypes.string,
  uppercase: PropTypes.bool,
  dataTestIds: PropTypes.shape({
    chip: PropTypes.string,
    deleteIcon: PropTypes.string
  })
};

export default Chip;
