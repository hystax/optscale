import React from "react";
import Invitations from "components/Invitations";
import InvitationsService from "services/InvitationsService";

const InvitationsContainer = () => {
  const { useGet } = InvitationsService();

  const { isLoading, invitations } = useGet();

  return <Invitations isLoading={isLoading} invitations={invitations} />;
};

InvitationsContainer.propTypes = {};

export default InvitationsContainer;
