import { useParams } from "react-router-dom";
import Button from "components/Button";
import { DeleteBIExportModal } from "components/SideModalManager/SideModals";
import { useOpenSideModal } from "hooks/useOpenSideModal";

const DeleteBIExport = () => {
  const { biExportId } = useParams();

  const openSideModal = useOpenSideModal();

  return (
    <Button
      dataTestId="btn_delete"
      variant="contained"
      color="error"
      messageId="delete"
      onClick={() => openSideModal(DeleteBIExportModal, { biExportId })}
    />
  );
};

export default DeleteBIExport;
