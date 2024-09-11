import DeleteEntity from "components/DeleteEntity";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import MlMetricsService from "services/MlMetricsService";

const DeleteMlMetricContainer = ({ id, name, onCancel }) => {
  const { isDemo } = useOrganizationInfo();

  const { useDeleteMlMetric } = MlMetricsService();

  const { onDelete, isLoading } = useDeleteMlMetric();

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

export default DeleteMlMetricContainer;
