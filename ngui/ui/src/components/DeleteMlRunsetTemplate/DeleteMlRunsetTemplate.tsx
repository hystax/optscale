import { useParams } from "react-router-dom";
import Button from "components/Button";
import { DeleteMlRunsetTemplateModal } from "components/SideModalManager/SideModals";
import { useOpenSideModal } from "hooks/useOpenSideModal";

const DeleteMlRunsetTemplate = () => {
  const { templateId } = useParams();

  const openSideModal = useOpenSideModal();

  return (
    <Button
      dataTestId="btn_delete"
      variant="contained"
      color="error"
      messageId="delete"
      onClick={() => openSideModal(DeleteMlRunsetTemplateModal, { runsetTemplateId: templateId })}
    />
  );
};

export default DeleteMlRunsetTemplate;
