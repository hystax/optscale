import Invitations from "components/Invitations";
import InvitationsService from "services/InvitationsService";

const InvitationsContainer = () => {
  const { useGet } = InvitationsService();

  const { isLoading, invitations } = useGet();

  return <Invitations isLoading={isLoading} invitations={invitations} />;
};

export default InvitationsContainer;
