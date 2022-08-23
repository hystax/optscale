import React from "react";
import PropTypes from "prop-types";
import BaseLayout from "layouts/BaseLayout";

const MainLayout = ({ children }) => (
  <BaseLayout showOrganizationSelector showMainMenu>
    {children}
  </BaseLayout>
);

MainLayout.propTypes = {
  children: PropTypes.node.isRequired
};

export default MainLayout;
