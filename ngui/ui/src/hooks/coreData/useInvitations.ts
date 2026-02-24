import { useInvitationsQuery } from "graphql/__generated__/hooks/restapi";
import { useOrganizationInfo } from "../useOrganizationInfo";

export const useInvitations = () => {
  const { organizationId } = useOrganizationInfo();

  const { data: { invitations = [] } = {} } = useInvitationsQuery({
    variables: {
      organizationId,
    },
    fetchPolicy: "cache-only",
  });

  return invitations;
};
