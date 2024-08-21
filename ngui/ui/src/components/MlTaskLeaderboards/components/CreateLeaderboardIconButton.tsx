import AddOutlinedIcon from "@mui/icons-material/AddOutlined";
import IconButton from "components/IconButton";
import { CreateLeaderboardModal } from "components/SideModalManager/SideModals";
import { useOpenSideModal } from "hooks/useOpenSideModal";

const CreateLeaderboardIconButton = ({ leaderboardTemplate, task, onSuccess }) => {
  const openSideModal = useOpenSideModal();

  return (
    <IconButton
      icon={<AddOutlinedIcon fontSize="small" />}
      tooltip={{
        show: true,
        messageId: "add"
      }}
      onClick={() => openSideModal(CreateLeaderboardModal, { leaderboardTemplate, task, onSuccess })}
    />
  );
};

export default CreateLeaderboardIconButton;
