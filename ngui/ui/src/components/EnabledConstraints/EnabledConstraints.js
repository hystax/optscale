import React, { Fragment } from "react";
import PropTypes from "prop-types";
import { useConstraints } from "hooks/useConstraints";

const EnabledConstraints = ({ render }) => {
  const enabledConstraints = useConstraints();

  return enabledConstraints.map((type) => <Fragment key={type}>{render(type)}</Fragment>);
};

EnabledConstraints.propTypes = {
  render: PropTypes.func.isRequired
};

export default EnabledConstraints;
