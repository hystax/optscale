import DeleteEntity from "components/DeleteEntity";
import MlLeaderboardsService from "services/MlLeaderboardsService";

const DeleteLeaderboardDatasetContainer = ({ leaderboardDataset, onSuccess, onCancel }) => {
  const { useDeleteLeaderboardDataset } = MlLeaderboardsService();
  const { isLoading: isDeleteLeaderboardDatasetLoading, onDelete } = useDeleteLeaderboardDataset();

  return (
    <DeleteEntity
      onCancel={onCancel}
      deleteButtonProps={{
        onDelete: () => onDelete(leaderboardDataset.id).then(onSuccess)
      }}
      isLoading={isDeleteLeaderboardDatasetLoading}
      dataTestIds={{
        text: "p_delete",
        deleteButton: "btn_smodal_delete",
        cancelButton: "btn_cancel"
      }}
      message={{
        messageId: "deleteLeaderboardCriteriaQuestion",
        values: {
          name: leaderboardDataset.name
        }
      }}
    />
  );
};

export default DeleteLeaderboardDatasetContainer;
