import EditOutlinedIcon from "@mui/icons-material/EditOutlined";
import IconButton from "components/IconButton";
import { EditLeaderboardModal } from "components/SideModalManager/SideModals";
import { useOpenSideModal } from "hooks/useOpenSideModal";

const EditLeaderboardIconButton = ({ task, leaderboard, onSuccess }) => {
  const openSideModal = useOpenSideModal();

  return (
    <IconButton
      icon={<EditOutlinedIcon fontSize="small" />}
      tooltip={{
        show: true,
        messageId: "edit"
      }}
      onClick={() => openSideModal(EditLeaderboardModal, { task, leaderboard, onSuccess })}
    />
  );
};

export default EditLeaderboardIconButton;
