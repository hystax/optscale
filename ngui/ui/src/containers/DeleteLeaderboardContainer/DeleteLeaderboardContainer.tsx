import DeleteEntity from "components/DeleteEntity";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import MlLeaderboardsService from "services/MlLeaderboardsService";

const DeleteLeaderboardContainer = ({ leaderboard, onSuccess, onCancel }) => {
  const { isDemo } = useOrganizationInfo();

  const { useDeleteLeaderboard } = MlLeaderboardsService();
  const { isLoading: isDeleteLeaderboardLoading, onDelete } = useDeleteLeaderboard();

  return (
    <DeleteEntity
      onCancel={onCancel}
      deleteButtonProps={{
        onDelete: () => onDelete(leaderboard.id).then(onSuccess),
        disabled: isDemo,
        tooltip: {
          show: isDemo,
          messageId: "notAvailableInLiveDemo"
        }
      }}
      isLoading={isDeleteLeaderboardLoading}
      dataTestIds={{
        text: "p_delete",
        deleteButton: "btn_smodal_delete",
        cancelButton: "btn_cancel"
      }}
      message={{
        messageId: "deleteLeaderboardQuestion",
        values: {
          name: leaderboard.name
        }
      }}
    />
  );
};

export default DeleteLeaderboardContainer;
