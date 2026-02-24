import { useOrganizationThemeSettingsQuery } from "graphql/__generated__/hooks/restapi";
import { useOrganizationInfo } from "../useOrganizationInfo";

export const useOrganizationThemeSettings = () => {
  const { organizationId } = useOrganizationInfo();

  const { data: { organizationThemeSettings = {} } = {} } = useOrganizationThemeSettingsQuery({
    fetchPolicy: "cache-only",
    variables: {
      organizationId,
    },
  });

  return organizationThemeSettings;
};
