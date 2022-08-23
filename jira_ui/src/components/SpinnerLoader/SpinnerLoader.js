import React from "react";
import Spinner from "@atlaskit/spinner";
import PropTypes from "prop-types";

const SpinnerLoader = ({ height = "200px", size = 50 }) => (
  <div
    style={{
      minWidth: "200px",
      height,
      display: "flex",
      justifyContent: "center",
      alignItems: "center"
    }}
  >
    <Spinner size={size} />
  </div>
);

SpinnerLoader.propTypes = {
  height: PropTypes.string,
  size: PropTypes.number
};

export default SpinnerLoader;
