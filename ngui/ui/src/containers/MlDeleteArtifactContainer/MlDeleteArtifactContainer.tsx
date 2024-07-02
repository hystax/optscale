import DeleteEntity from "components/DeleteEntity";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import MlArtifactsService from "services/MlArtifactsService";

type MlDeleteArtifactContainerProps = {
  id: string;
  name: string;
  onSuccess: () => void;
  closeSideModal: () => void;
};

const MlDeleteArtifactContainer = ({ id, name, onSuccess, closeSideModal }: MlDeleteArtifactContainerProps) => {
  const { isDemo } = useOrganizationInfo();

  const { useDelete } = MlArtifactsService();
  const { onDelete, isLoading } = useDelete();

  const onDatasetDelete = () => {
    onDelete(id).then(() => {
      onSuccess();
      closeSideModal();
    });
  };

  return (
    <DeleteEntity
      onCancel={closeSideModal}
      isLoading={isLoading}
      deleteButtonProps={{
        onDelete: onDatasetDelete,
        disabled: isDemo,
        tooltip: { show: isDemo, messageId: "notAvailableInLiveDemo" }
      }}
      dataTestIds={{
        text: "p_delete",
        deleteButton: "btn_smodal_delete",
        cancelButton: "btn_cancel"
      }}
      message={{
        messageId: "deleteMlArtifactQuestion",
        values: {
          name,
          strong: (chunks) => <strong>{chunks}</strong>
        }
      }}
    />
  );
};

export default MlDeleteArtifactContainer;
