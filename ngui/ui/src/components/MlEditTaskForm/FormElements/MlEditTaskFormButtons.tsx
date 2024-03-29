import { Box } from "@mui/material";
import Button from "components/Button";
import ButtonLoader from "components/ButtonLoader";
import FormButtonsWrapper from "components/FormButtonsWrapper";
import { MlDeleteTaskModal } from "components/SideModalManager/SideModals";
import { useOpenSideModal } from "hooks/useOpenSideModal";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";

const DeleteTaskButton = ({ id, name }) => {
  const openSideModal = useOpenSideModal();

  return (
    <Button
      dataTestId="btn_delete"
      variant="contained"
      color="error"
      messageId="delete"
      onClick={() =>
        openSideModal(MlDeleteTaskModal, {
          name,
          id
        })
      }
    />
  );
};

const MlEditTaskFormButtons = ({ taskId, taskName, onCancel, isLoading = false }) => {
  const { isDemo } = useOrganizationInfo();

  return (
    <FormButtonsWrapper justifyContent="space-between">
      <Box display="flex">
        <ButtonLoader
          messageId="save"
          dataTestId="btn_save"
          color="primary"
          variant="contained"
          type="submit"
          disabled={isDemo}
          isLoading={isLoading}
          tooltip={{ show: isDemo, messageId: "notAvailableInLiveDemo" }}
        />
        <Button messageId="cancel" dataTestId="btn_cancel" onClick={onCancel} />
      </Box>
      <DeleteTaskButton id={taskId} name={taskName} />
    </FormButtonsWrapper>
  );
};

export default MlEditTaskFormButtons;
