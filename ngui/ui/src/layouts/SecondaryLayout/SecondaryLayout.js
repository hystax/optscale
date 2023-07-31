import React from "react";
import PropTypes from "prop-types";
import BaseLayout from "layouts/BaseLayout";

const SecondaryLayout = ({ children }) => <BaseLayout>{children}</BaseLayout>;

SecondaryLayout.propTypes = {
  children: PropTypes.node.isRequired
};

export default SecondaryLayout;
