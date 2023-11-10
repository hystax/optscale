import { useNavigate } from "react-router-dom";
import DeleteEntity from "components/DeleteEntity";
import BIExportService from "services/BIExportService";
import { BI_EXPORTS } from "urls";

const DeleteBIExportContainer = ({ id, onCancel }) => {
  const navigate = useNavigate();

  const { useDelete } = BIExportService();

  const { onDelete, isLoading } = useDelete();

  const onSubmit = () => onDelete(id).then(() => navigate(BI_EXPORTS));

  return (
    <DeleteEntity
      onDelete={onSubmit}
      onCancel={onCancel}
      isLoading={isLoading}
      deleteButtonProps={{
        color: "error",
        variant: "contained",
        onDelete: onSubmit
      }}
      dataTestIds={{
        text: "p_delete_bi_export",
        deleteButton: "btn_delete_bi_export_delete",
        cancelButton: "btn_delete_bi_export_cancel"
      }}
      message={{
        messageId: "deleteBIExportQuestion"
      }}
    />
  );
};

export default DeleteBIExportContainer;
