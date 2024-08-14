import FileCopyOutlinedIcon from "@mui/icons-material/FileCopyOutlined";
import IconButton from "components/IconButton";
import { CloneLeaderboardDatasetModal } from "components/SideModalManager/SideModals";
import { useOpenSideModal } from "hooks/useOpenSideModal";

const CopyLeaderboardDatasetIconButton = ({ task, leaderboard, leaderboardDataset, onSuccess }) => {
  const openSideModal = useOpenSideModal();

  return (
    <IconButton
      icon={<FileCopyOutlinedIcon fontSize="small" />}
      tooltip={{
        show: true,
        messageId: "clone"
      }}
      onClick={() => openSideModal(CloneLeaderboardDatasetModal, { task, leaderboard, leaderboardDataset, onSuccess })}
    />
  );
};

export default CopyLeaderboardDatasetIconButton;
