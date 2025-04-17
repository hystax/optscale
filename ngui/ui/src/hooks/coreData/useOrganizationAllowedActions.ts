import { useQuery } from "@apollo/client";
import { GET_ORGANIZATION_ALLOWED_ACTIONS } from "graphql/api/auth/queries";
import { useOrganizationInfo } from "../useOrganizationInfo";

export const useOrganizationAllowedActions = () => {
  const { organizationId } = useOrganizationInfo();

  const { data: { organizationAllowedActions = {} } = {} } = useQuery(GET_ORGANIZATION_ALLOWED_ACTIONS, {
    fetchPolicy: "cache-only",
    variables: {
      requestParams: {
        organization: organizationId
      }
    }
  });

  return organizationAllowedActions;
};
