import ContentBackdropLoader from "components/ContentBackdropLoader";
import {
  OrganizationThemeSettingsDocument,
  useUpdateOrganizationThemeSettingsMutation,
} from "graphql/__generated__/hooks/restapi";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";

const OrganizationThemeSettingsContainer = ({ children }) => {
  const { organizationId } = useOrganizationInfo();

  const [updateOrganizationThemeSettingsMutation, { loading }] = useUpdateOrganizationThemeSettingsMutation({
    update: (cache, { data: { updateOrganizationThemeSettings } }) => {
      cache.writeQuery({
        query: OrganizationThemeSettingsDocument,
        variables: { organizationId },
        data: {
          organizationThemeSettings: updateOrganizationThemeSettings,
        },
      });
    },
  });

  const onUpdate = (data) =>
    updateOrganizationThemeSettingsMutation({
      variables: {
        organizationId,
        value: data,
      },
    });

  return <ContentBackdropLoader isLoading={loading}>{children(onUpdate)}</ContentBackdropLoader>;
};

export default OrganizationThemeSettingsContainer;
