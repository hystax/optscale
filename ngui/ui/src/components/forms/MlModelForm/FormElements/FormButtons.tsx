import { Box } from "@mui/material";
import { useNavigate } from "react-router-dom";
import Button from "components/Button";
import ButtonLoader from "components/ButtonLoader";
import FormButtonsWrapper from "components/FormButtonsWrapper";
import { DeleteMlModelModal } from "components/SideModalManager/SideModals";
import { useOpenSideModal } from "hooks/useOpenSideModal";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { ML_MODELS } from "urls";

type MlModelFormButtonsProps = {
  onCancel: () => void;
  isLoading?: boolean;
};

type MlEditModelFormButtonsProps = MlModelFormButtonsProps & {
  modelName: string;
  modelId: string;
};

type MlCreateModelFormButtonsProps = MlModelFormButtonsProps;

type SaveButtonProps = {
  isLoading: MlModelFormButtonsProps["isLoading"];
};

type CloseButtonProps = {
  onCancel: MlModelFormButtonsProps["onCancel"];
};

const SaveButton = ({ isLoading }: SaveButtonProps) => {
  const { isDemo } = useOrganizationInfo();

  return (
    <ButtonLoader
      messageId="save"
      dataTestId="btn_save"
      color="primary"
      variant="contained"
      type="submit"
      disabled={isDemo}
      tooltip={{ show: isDemo, messageId: "notAvailableInLiveDemo" }}
      isLoading={isLoading}
    />
  );
};

const CloseButton = ({ onCancel }: CloseButtonProps) => (
  <Button messageId="cancel" dataTestId="btn_cancel" onClick={onCancel} />
);

const EditFormButtons = ({
  modelName,
  modelId,
  onCancel,
  isLoading = false
}: MlEditModelFormButtonsProps & {
  modelName: string;
  modelId: string;
}) => {
  const navigate = useNavigate();
  const openSideModal = useOpenSideModal();

  const onSuccess = () => navigate(ML_MODELS);

  return (
    <FormButtonsWrapper justifyContent="space-between">
      <Box display="flex">
        <SaveButton isLoading={isLoading} />
        <CloseButton onCancel={onCancel} />
      </Box>
      <Button
        dataTestId="btn_delete"
        variant="contained"
        color="error"
        messageId="delete"
        onClick={() => openSideModal(DeleteMlModelModal, { modelId, modelName, onSuccess })}
      />
    </FormButtonsWrapper>
  );
};

const CreateFormButtons = ({ onCancel, isLoading = false }: MlCreateModelFormButtonsProps) => (
  <FormButtonsWrapper>
    <SaveButton isLoading={isLoading} />
    <CloseButton onCancel={onCancel} />
  </FormButtonsWrapper>
);

export { EditFormButtons, CreateFormButtons };
