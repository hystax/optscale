import DeleteOutlinedIcon from "@mui/icons-material/DeleteOutlined";
import IconButton from "components/IconButton";
import { DeleteWebhookModal } from "components/SideModalManager/SideModals";
import { useOpenSideModal } from "hooks/useOpenSideModal";
import { useOrganizationActionRestrictions } from "hooks/useOrganizationActionRestrictions";

const DeleteWebhook = ({ id, action, url }) => {
  const openSideModal = useOpenSideModal();

  const { isRestricted, restrictionReasonMessage } = useOrganizationActionRestrictions();

  return (
    <IconButton
      color="error"
      icon={<DeleteOutlinedIcon />}
      onClick={() => openSideModal(DeleteWebhookModal, { id, action, url })}
      disabled={isRestricted}
      tooltip={{
        show: isRestricted,
        value: restrictionReasonMessage,
      }}
    />
  );
};

export default DeleteWebhook;
