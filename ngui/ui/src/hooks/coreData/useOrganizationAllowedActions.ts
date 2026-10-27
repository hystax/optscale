import { useOrganizationAllowedActionsQuery } from "graphql/__generated__/hooks/auth";
import { useOrganizationInfo } from "../useOrganizationInfo";

export const useOrganizationAllowedActions = () => {
  const { organizationId } = useOrganizationInfo();

  const { data: { organizationAllowedActions = {} } = {} } = useOrganizationAllowedActionsQuery({
    fetchPolicy: "cache-only",
    variables: {
      requestParams: {
        organization: organizationId,
      },
    },
  });

  return organizationAllowedActions;
};
