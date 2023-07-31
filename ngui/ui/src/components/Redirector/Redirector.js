import React from "react";
import PropTypes from "prop-types";
import { Navigate } from "react-router-dom";

const Redirector = ({ children = null, condition, to, replace = false }) =>
  condition ? <Navigate replace={replace} to={to} /> : children;

Redirector.propTypes = {
  condition: PropTypes.bool.isRequired,
  to: PropTypes.string.isRequired,
  children: PropTypes.node,
  replace: PropTypes.bool
};

export default Redirector;
