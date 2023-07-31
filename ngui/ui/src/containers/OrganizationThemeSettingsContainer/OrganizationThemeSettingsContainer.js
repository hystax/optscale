import React from "react";
import PropTypes from "prop-types";
import ContentBackdropLoader from "components/ContentBackdropLoader";
import OrganizationOptionsService from "services/OrganizationOptionsService";

const OrganizationThemeSettingsContainer = ({ children }) => {
  const { useUpdateThemeSettings } = OrganizationOptionsService();
  const { update, isLoading } = useUpdateThemeSettings();

  const onUpdate = (data) => {
    update(data);
  };

  return <ContentBackdropLoader isLoading={isLoading}>{children(onUpdate)}</ContentBackdropLoader>;
};

OrganizationThemeSettingsContainer.propTypes = {
  children: PropTypes.func.isRequired
};

export default OrganizationThemeSettingsContainer;
