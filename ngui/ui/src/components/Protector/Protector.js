import React from "react";
import PropTypes from "prop-types";
import Error from "components/Error";
import { useIsAllowed } from "hooks/useAllowedActions";

const Protector = ({ children, allowedActions = [] }) => {
  const shouldRenderChildren = useIsAllowed({ requiredActions: allowedActions });

  return shouldRenderChildren ? children : <Error messageId="forbidden" />;
};

Protector.propTypes = {
  children: PropTypes.node.isRequired,
  allowedActions: PropTypes.array
};

export default Protector;
