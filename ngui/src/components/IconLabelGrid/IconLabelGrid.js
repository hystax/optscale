import React from "react";
import Grid from "@mui/material/Grid";
import PropTypes from "prop-types";
import { SPACING_1 } from "utils/layouts";

const IconLabelGrid = ({ startIcon, label, endIcon }) => (
  <Grid container spacing={SPACING_1} alignItems="center" wrap="nowrap">
    {startIcon}
    <Grid item>{label}</Grid>
    {endIcon}
  </Grid>
);

IconLabelGrid.propTypes = {
  label: PropTypes.node.isRequired,
  startIcon: PropTypes.node,
  endIcon: PropTypes.node
};

export default IconLabelGrid;
