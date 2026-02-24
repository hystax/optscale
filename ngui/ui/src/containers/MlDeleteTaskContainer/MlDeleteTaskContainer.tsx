import { useNavigate } from "react-router-dom";
import DeleteEntity from "components/DeleteEntity";
import { useOrganizationActionRestrictions } from "hooks/useOrganizationActionRestrictions";
import MlTasksService from "services/MlTasksService";
import { ML_TASKS } from "urls";

const MlDeleteTaskContainer = ({ name, id, onCancel }) => {
  const navigate = useNavigate();

  const { isRestricted, restrictionReasonMessage } = useOrganizationActionRestrictions();

  const { useDeleteTask } = MlTasksService();
  const { onDelete, isLoading } = useDeleteTask();

  const redirectToTasksOverview = () => navigate(ML_TASKS);

  const onTaskDelete = () => {
    onDelete(id).then(() => {
      redirectToTasksOverview();
    });
  };

  return (
    <DeleteEntity
      onCancel={onCancel}
      isLoading={isLoading}
      deleteButtonProps={{
        onDelete: onTaskDelete,
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
        messageId: "deleteMlTaskQuestion",
        values: {
          task: name,
          strong: (chunks) => <strong>{chunks}</strong>,
        },
      }}
    />
  );
};

export default MlDeleteTaskContainer;
