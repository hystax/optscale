import React from "react";
import CancelIcon from "@mui/icons-material/Cancel";
import MuiChip from "@mui/material/Chip";
import PropTypes from "prop-types";
import useStyles from "./Chip.styles";

const Chip = ({
  color = "info",
  variant = "filled",
  size = "small",
  uppercase = false,
  dataTestIds = {},
  stopMouseDownPropagationOnDelete = false, // use case: when chip is inside selector value, need to delete chip, not to open selector
  multiline = false,
  className,
  ...rest
}) => {
  const { classes, cx } = useStyles();

  const chipClasses = cx(classes.chip, uppercase ? classes.uppercase : "", multiline ? classes.multiline : "", className);

  const { chip: chipDataTestId, deleteIcon: deleteIconDataTestId } = dataTestIds;

  return (
    <MuiChip
      {...rest}
      variant={variant}
      color={color}
      deleteIcon={
        <CancelIcon
          data-test-id={deleteIconDataTestId}
          onMouseDown={stopMouseDownPropagationOnDelete ? (e) => e.stopPropagation() : undefined}
        />
      }
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
  stopMouseDownPropagationOnDelete: PropTypes.bool,
  multiline: PropTypes.bool,
  dataTestIds: PropTypes.shape({
    chip: PropTypes.string,
    deleteIcon: PropTypes.string
  }),
  className: PropTypes.string
};

export default Chip;
