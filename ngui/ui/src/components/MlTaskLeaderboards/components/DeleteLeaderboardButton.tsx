import DeleteOutlinedIcon from "@mui/icons-material/DeleteOutlined";
import IconButton from "components/IconButton";
import { DeleteLeaderboardModal } from "components/SideModalManager/SideModals";
import { useOpenSideModal } from "hooks/useOpenSideModal";

const DeleteLeaderboardButton = ({ leaderboard }) => {
  const openSideModal = useOpenSideModal();

  return (
    <IconButton
      icon={<DeleteOutlinedIcon fontSize="small" />}
      color="error"
      tooltip={{
        show: true,
        messageId: "delete"
      }}
      onClick={() => openSideModal(DeleteLeaderboardModal, { leaderboard })}
    />
  );
};

export default DeleteLeaderboardButton;
