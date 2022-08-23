import React from "react";
import CancelIcon from "@mui/icons-material/Cancel";
import MuiChip from "@mui/material/Chip";
import PropTypes from "prop-types";
import { capitalize } from "utils/strings";
import useStyles from "./Chip.styles";

const Chip = ({ color = "info", variant = "default", size = "small", uppercase = false, dataTestIds = {}, ...rest }) => {
  const { classes, cx } = useStyles();

  const colorClass = classes["".concat(variant).concat(capitalize(color))];

  const chipClasses = cx(classes.chip, colorClass, uppercase ? classes.uppercase : "");

  const { chip: chipDataTestId, deleteIcon: deleteIconDataTestId } = dataTestIds;

  return (
    <MuiChip
      {...rest}
      deleteIcon={<CancelIcon data-test-id={deleteIconDataTestId} />}
      data-test-id={chipDataTestId}
      className={chipClasses}
      size={size}
    />
  );
};

Chip.propTypes = {
  color: PropTypes.oneOf(["info", "primary", "success", "error", "warning"]),
  variant: PropTypes.oneOf(["default", "outlined"]),
  size: PropTypes.oneOf(["small", "medium"]),
  uppercase: PropTypes.bool,
  dataTestIds: PropTypes.shape({
    chip: PropTypes.string,
    deleteIcon: PropTypes.string
  })
};

export default Chip;
