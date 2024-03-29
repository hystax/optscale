import DeleteEntity from "components/DeleteEntity";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import MlTasksService from "services/MlTasksService";

const DeleteMlGlobalMetricContainer = ({ id, name, onCancel }) => {
  const { isDemo } = useOrganizationInfo();

  const { useDeleteGlobalMetric } = MlTasksService();

  const { onDelete, isLoading } = useDeleteGlobalMetric();

  const onDeleteHandler = () => onDelete(id).then(() => onCancel());

  return (
    <DeleteEntity
      onCancel={onCancel}
      isLoading={isLoading}
      deleteButtonProps={{
        onDelete: onDeleteHandler,
        disabled: isDemo,
        tooltip: { show: isDemo, messageId: "notAvailableInLiveDemo" }
      }}
      dataTestIds={{
        text: "p_delete",
        deleteButton: "btn_smodal_delete",
        cancelButton: "btn_cancel"
      }}
      message={{
        messageId: "deleteMetricQuestion",
        values: {
          name
        }
      }}
    />
  );
};

export default DeleteMlGlobalMetricContainer;
