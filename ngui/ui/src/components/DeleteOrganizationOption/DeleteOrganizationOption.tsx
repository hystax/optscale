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

export default DeleteOrganizationOption;
