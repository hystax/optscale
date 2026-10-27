import DeleteEntity from "components/DeleteEntity";
import { useOrganizationActionRestrictions } from "hooks/useOrganizationActionRestrictions";
import MlMetricsService from "services/MlMetricsService";

const DeleteMlMetricContainer = ({ id, name, onCancel }) => {
  const { isRestricted, restrictionReasonMessage } = useOrganizationActionRestrictions();

  const { useDeleteMlMetric } = MlMetricsService();

  const { onDelete, isLoading } = useDeleteMlMetric();

  const onDeleteHandler = () => onDelete(id).then(() => onCancel());

  return (
    <DeleteEntity
      onCancel={onCancel}
      isLoading={isLoading}
      deleteButtonProps={{
        onDelete: onDeleteHandler,
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
        messageId: "deleteMetricQuestion",
        values: {
          name,
        },
      }}
    />
  );
};

export default DeleteMlMetricContainer;
