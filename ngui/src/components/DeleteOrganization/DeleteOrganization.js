import React from "react";
import Button from "components/Button";
import { DeleteOrganizationModal } from "components/SideModalManager/SideModals";
import { useOpenSideModal } from "hooks/useOpenSideModal";

const DeleteOrganization = () => {
  const openSideModal = useOpenSideModal();

  return <Button messageId="delete" color="error" variant="contained" onClick={() => openSideModal(DeleteOrganizationModal)} />;
};

export default DeleteOrganization;
