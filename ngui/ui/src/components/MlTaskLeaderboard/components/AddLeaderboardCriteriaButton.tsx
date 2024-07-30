import AddOutlinedIcon from "@mui/icons-material/AddOutlined";
import Button from "components/Button";
import { CreateLeaderboardDatasetModal } from "components/SideModalManager/SideModals";
import { useOpenSideModal } from "hooks/useOpenSideModal";

const AddLeaderboardCriteriaButton = ({ leaderboard, task, sx }) => {
  const openSideModal = useOpenSideModal();

  return (
    <Button
      messageId="add"
      startIcon={<AddOutlinedIcon />}
      sx={sx}
      onClick={() => openSideModal(CreateLeaderboardDatasetModal, { leaderboard, task })}
    />
  );
};

export default AddLeaderboardCriteriaButton;
