import DeleteOutlinedIcon from "@mui/icons-material/DeleteOutlined";
import IconButton from "components/IconButton";
import { DeleteLeaderboardCriteriaModal } from "components/SideModalManager/SideModals";
import { useOpenSideModal } from "hooks/useOpenSideModal";

const DeleteLeaderboardDatasetButton = ({ leaderboardDataset }) => {
  const openSideModal = useOpenSideModal();

  return (
    <IconButton
      icon={<DeleteOutlinedIcon fontSize="small" />}
      color="error"
      tooltip={{
        show: true,
        messageId: "delete"
      }}
      onClick={() => openSideModal(DeleteLeaderboardCriteriaModal, { leaderboardDataset })}
    />
  );
};

export default DeleteLeaderboardDatasetButton;
