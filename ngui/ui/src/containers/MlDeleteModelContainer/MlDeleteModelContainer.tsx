import { useNavigate } from "react-router-dom";
import DeleteEntity from "components/DeleteEntity";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import MlModelsService from "services/MlModelsService";
import { ML_MODELS } from "urls";

const MlDeleteModelContainer = ({ name, id, onCancel }) => {
  const navigate = useNavigate();
  const { isDemo } = useOrganizationInfo();

  const { useDeleteModel } = MlModelsService();
  const { onDelete, isLoading } = useDeleteModel();

  const redirectToModelsOverview = () => navigate(ML_MODELS);

  const onModelDelete = () => {
    onDelete(id).then(() => {
      redirectToModelsOverview();
    });
  };

  return (
    <DeleteEntity
      onCancel={onCancel}
      isLoading={isLoading}
      deleteButtonProps={{
        onDelete: onModelDelete,
        disabled: isDemo,
        tooltip: { show: isDemo, messageId: "notAvailableInLiveDemo" }
      }}
      dataTestIds={{
        text: "p_delete",
        deleteButton: "btn_smodal_delete",
        cancelButton: "btn_cancel"
      }}
      message={{
        messageId: "deleteMlModelQuestion",
        values: {
          model: name,
          strong: (chunks) => <strong>{chunks}</strong>
        }
      }}
    />
  );
};

export default MlDeleteModelContainer;
