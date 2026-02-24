import DeleteEntity from "components/DeleteEntity";
import { useOrganizationActionRestrictions } from "hooks/useOrganizationActionRestrictions";
import MlDatasetsService from "services/MlDatasetsService";

const MlDeleteDatasetContainer = ({ path, id, closeSideModal }) => {
  const { isRestricted, restrictionReasonMessage } = useOrganizationActionRestrictions();

  const { useDelete } = MlDatasetsService();
  const { onDelete, isLoading } = useDelete();

  const onDatasetDelete = () => {
    onDelete(id).then(() => {
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
        messageId: "deleteMlDatasetQuestion",
        values: {
          dataset: path,
          strong: (chunks) => <strong>{chunks}</strong>,
        },
      }}
    />
  );
};

export default MlDeleteDatasetContainer;
