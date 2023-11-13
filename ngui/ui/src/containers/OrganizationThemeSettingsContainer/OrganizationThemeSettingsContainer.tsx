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

export default OrganizationThemeSettingsContainer;
