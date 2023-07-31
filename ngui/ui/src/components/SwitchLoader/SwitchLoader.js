import React from "react";
import Switch from "@mui/material/Switch";
import PropTypes from "prop-types";
import Skeleton from "components/Skeleton";

const SwitchLoader = ({ fullWidth = false }) => (
  <Skeleton type="rect" fullWidth={fullWidth}>
    <Switch />
  </Skeleton>
);

SwitchLoader.propTypes = {
  fullWidth: PropTypes.bool
};

export default SwitchLoader;
