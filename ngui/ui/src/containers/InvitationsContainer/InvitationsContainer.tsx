import { NetworkStatus } from "@apollo/client";
import Invitations from "components/Invitations";
import { useInvitationsQuery, useOrganizationsLazyQuery } from "graphql/__generated__/hooks/restapi";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";

const InvitationsContainer = () => {
  const { organizationId } = useOrganizationInfo();

  const {
    data: { invitations = [] } = {},
    networkStatus,
    refetch: refetchInvitations,
  } = useInvitationsQuery({
    variables: {
      organizationId,
    },
    notifyOnNetworkStatusChange: true,
  });

  const [getOrganizations] = useOrganizationsLazyQuery({
    fetchPolicy: "network-only",
  });

  const isLoading = networkStatus === NetworkStatus.loading || networkStatus === NetworkStatus.refetch;

  const onSuccess = () => {
    refetchInvitations();
    getOrganizations();
  };

  return (
    <Invitations invitations={invitations} isLoading={isLoading} onSuccessAccept={onSuccess} onSuccessDecline={onSuccess} />
  );
};

export default InvitationsContainer;
