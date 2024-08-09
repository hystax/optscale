import AddOutlinedIcon from "@mui/icons-material/AddOutlined";
import IconButton from "components/IconButton";
import { CreateLeaderboardDatasetModal } from "components/SideModalManager/SideModals";
import { useOpenSideModal } from "hooks/useOpenSideModal";

const AddLeaderboardCriteriaButton = ({ leaderboard, task }) => {
  const openSideModal = useOpenSideModal();

  return (
    <IconButton
      icon={<AddOutlinedIcon fontSize="small" />}
      tooltip={{
        show: true,
        messageId: "add"
      }}
      onClick={() => openSideModal(CreateLeaderboardDatasetModal, { leaderboard, task })}
    />
  );
};

export default AddLeaderboardCriteriaButton;
