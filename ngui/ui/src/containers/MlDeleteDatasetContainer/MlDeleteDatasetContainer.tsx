import DeleteEntity from "components/DeleteEntity";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import MlDatasetsService from "services/MlDatasetsService";

const MlDeleteDatasetContainer = ({ path, id, closeSideModal }) => {
  const { isDemo } = useOrganizationInfo();

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
        disabled: isDemo,
        tooltip: { show: isDemo, messageId: "notAvailableInLiveDemo" }
      }}
      dataTestIds={{
        text: "p_delete",
        deleteButton: "btn_smodal_delete",
        cancelButton: "btn_cancel"
      }}
      message={{
        messageId: "deleteMlDatasetQuestion",
        values: {
          dataset: path,
          strong: (chunks) => <strong>{chunks}</strong>
        }
      }}
    />
  );
};

export default MlDeleteDatasetContainer;
