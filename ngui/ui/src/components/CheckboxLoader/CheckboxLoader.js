import React from "react";
import Checkbox from "@mui/material/Checkbox";
import PropTypes from "prop-types";
import Skeleton from "components/Skeleton";

const CheckboxLoader = ({ fullWidth = false }) => (
  <Skeleton type="rect" fullWidth={fullWidth}>
    <Checkbox />
  </Skeleton>
);

CheckboxLoader.propTypes = {
  fullWidth: PropTypes.bool
};

export default CheckboxLoader;
