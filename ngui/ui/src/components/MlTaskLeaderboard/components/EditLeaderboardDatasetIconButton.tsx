import EditOutlinedIcon from "@mui/icons-material/EditOutlined";
import IconButton from "components/IconButton";
import { EditLeaderboardDatasetModal } from "components/SideModalManager/SideModals";
import { useOpenSideModal } from "hooks/useOpenSideModal";

const EditLeaderboardDatasetIconButton = ({ task, leaderboardDataset, onSuccess }) => {
  const openSideModal = useOpenSideModal();

  return (
    <IconButton
      icon={<EditOutlinedIcon fontSize="small" />}
      tooltip={{
        show: true,
        messageId: "edit"
      }}
      onClick={() => openSideModal(EditLeaderboardDatasetModal, { task, leaderboardDataset, onSuccess })}
    />
  );
};

export default EditLeaderboardDatasetIconButton;
