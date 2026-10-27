import DeleteEntity from "components/DeleteEntity";
import { useOrganizationActionRestrictions } from "hooks/useOrganizationActionRestrictions";
import MlLeaderboardsService from "services/MlLeaderboardsService";

const DeleteLeaderboardContainer = ({ leaderboard, onSuccess, onCancel }) => {
  const { isRestricted, restrictionReasonMessage } = useOrganizationActionRestrictions();

  const { useDeleteLeaderboard } = MlLeaderboardsService();
  const { isLoading: isDeleteLeaderboardLoading, onDelete } = useDeleteLeaderboard();

  return (
    <DeleteEntity
      onCancel={onCancel}
      deleteButtonProps={{
        onDelete: () => onDelete(leaderboard.id).then(onSuccess),
        disabled: isRestricted,
        tooltip: {
          show: isRestricted,
          value: restrictionReasonMessage,
        },
      }}
      isLoading={isDeleteLeaderboardLoading}
      dataTestIds={{
        text: "p_delete",
        deleteButton: "btn_smodal_delete",
        cancelButton: "btn_cancel",
      }}
      message={{
        messageId: "deleteLeaderboardQuestion",
        values: {
          name: leaderboard.name,
        },
      }}
    />
  );
};

export default DeleteLeaderboardContainer;
