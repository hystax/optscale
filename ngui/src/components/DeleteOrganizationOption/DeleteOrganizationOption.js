import React from "react";
import PropTypes from "prop-types";
import Button from "components/Button";
import { DeleteOrganizationOptionModal } from "components/SideModalManager/SideModals";
import { useOpenSideModal } from "hooks/useOpenSideModal";

const DeleteOrganizationOption = ({ name }) => {
  const openSideModal = useOpenSideModal();

  return (
    <Button
      messageId="delete"
      color="error"
      variant="contained"
      onClick={() => openSideModal(DeleteOrganizationOptionModal, { name })}
    />
  );
};

DeleteOrganizationOption.propTypes = {
  name: PropTypes.string.isRequired
};

export default DeleteOrganizationOption;
