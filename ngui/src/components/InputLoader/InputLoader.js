import React from "react";
import PropTypes from "prop-types";
import Input from "components/Input";
import Skeleton from "components/Skeleton";

const InputLoader = ({ margin = "dense", fullWidth }) => (
  <Skeleton type="rect" fullWidth={fullWidth}>
    <Input margin={margin} />
  </Skeleton>
);

InputLoader.propTypes = {
  fullWidth: PropTypes.bool,
  margin: PropTypes.string
};

export default InputLoader;
