import DeleteEntity from "components/DeleteEntity";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import MlLeaderboardsService from "services/MlLeaderboardsService";

const DeleteLeaderboardDatasetContainer = ({ leaderboardDataset, onSuccess, onCancel }) => {
  const { isDemo } = useOrganizationInfo();

  const { useDeleteLeaderboardDataset } = MlLeaderboardsService();
  const { isLoading: isDeleteLeaderboardDatasetLoading, onDelete } = useDeleteLeaderboardDataset();

  return (
    <DeleteEntity
      onCancel={onCancel}
      deleteButtonProps={{
        onDelete: () => onDelete(leaderboardDataset.id).then(onSuccess),
        disabled: isDemo,
        tooltip: {
          show: isDemo,
          messageId: "notAvailableInLiveDemo"
        }
      }}
      isLoading={isDeleteLeaderboardDatasetLoading}
      dataTestIds={{
        text: "p_delete",
        deleteButton: "btn_smodal_delete",
        cancelButton: "btn_cancel"
      }}
      message={{
        messageId: "deleteLeaderboardQuestion",
        values: {
          name: leaderboardDataset.name
        }
      }}
    />
  );
};

export default DeleteLeaderboardDatasetContainer;
