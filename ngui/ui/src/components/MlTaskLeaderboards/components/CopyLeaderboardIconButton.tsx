import FileCopyOutlinedIcon from "@mui/icons-material/FileCopyOutlined";
import IconButton from "components/IconButton";
import { CloneLeaderboardModal } from "components/SideModalManager/SideModals";
import { useOpenSideModal } from "hooks/useOpenSideModal";

const CopyLeaderboardIconButton = ({ task, leaderboardTemplate, leaderboard, onSuccess }) => {
  const openSideModal = useOpenSideModal();

  return (
    <IconButton
      icon={<FileCopyOutlinedIcon fontSize="small" />}
      tooltip={{
        show: true,
        messageId: "clone"
      }}
      onClick={() => openSideModal(CloneLeaderboardModal, { task, leaderboardTemplate, leaderboard, onSuccess })}
    />
  );
};

export default CopyLeaderboardIconButton;
