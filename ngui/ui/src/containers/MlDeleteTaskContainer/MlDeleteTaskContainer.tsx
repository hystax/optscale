import { useNavigate } from "react-router-dom";
import DeleteEntity from "components/DeleteEntity";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import MlTasksService from "services/MlTasksService";
import { ML_TASKS } from "urls";

const MlDeleteTaskContainer = ({ name, id, onCancel }) => {
  const navigate = useNavigate();
  const { isDemo } = useOrganizationInfo();

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
        disabled: isDemo,
        tooltip: { show: isDemo, messageId: "notAvailableInLiveDemo" }
      }}
      dataTestIds={{
        text: "p_delete",
        deleteButton: "btn_smodal_delete",
        cancelButton: "btn_cancel"
      }}
      message={{
        messageId: "deleteMlTaskQuestion",
        values: {
          task: name,
          strong: (chunks) => <strong>{chunks}</strong>
        }
      }}
    />
  );
};

export default MlDeleteTaskContainer;
