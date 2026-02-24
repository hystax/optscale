import DeleteEntity from "components/DeleteEntity";
import { useOrganizationActionRestrictions } from "hooks/useOrganizationActionRestrictions";
import MlArtifactsService from "services/MlArtifactsService";

type MlDeleteArtifactContainerProps = {
  id: string;
  name: string;
  onSuccess: () => void;
  closeSideModal: () => void;
};

const MlDeleteArtifactContainer = ({ id, name, onSuccess, closeSideModal }: MlDeleteArtifactContainerProps) => {
  const { isRestricted, restrictionReasonMessage } = useOrganizationActionRestrictions();

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
        disabled: isRestricted,
        tooltip: {
          show: isRestricted,
          value: restrictionReasonMessage,
        },
      }}
      dataTestIds={{
        text: "p_delete",
        deleteButton: "btn_smodal_delete",
        cancelButton: "btn_cancel",
      }}
      message={{
        messageId: "deleteMlArtifactQuestion",
        values: {
          name,
          strong: (chunks) => <strong>{chunks}</strong>,
        },
      }}
    />
  );
};

export default MlDeleteArtifactContainer;
