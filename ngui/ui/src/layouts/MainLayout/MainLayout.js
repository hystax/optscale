import React from "react";
import PropTypes from "prop-types";
import BaseLayout from "layouts/BaseLayout";

const MainLayout = ({ children, mainMenu }) => (
  <BaseLayout showOrganizationSelector showMainMenu mainMenu={mainMenu}>
    {children}
  </BaseLayout>
);

MainLayout.propTypes = {
  children: PropTypes.node.isRequired,
  mainMenu: PropTypes.array
};

export default MainLayout;
