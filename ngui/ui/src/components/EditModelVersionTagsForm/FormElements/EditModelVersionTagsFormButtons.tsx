import Button from "components/Button";
import ButtonLoader from "components/ButtonLoader";
import FormButtonsWrapper from "components/FormButtonsWrapper";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";

type EditModelVersionTagsFormButtonsProps = {
  onCancel: () => void;
  isLoading?: boolean;
};

const EditModelVersionTagsFormButtons = ({ onCancel, isLoading = false }: EditModelVersionTagsFormButtonsProps) => {
  const { isDemo } = useOrganizationInfo();

  return (
    <FormButtonsWrapper>
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
      <Button messageId="cancel" dataTestId="btn_cancel" onClick={onCancel} />
    </FormButtonsWrapper>
  );
};

export default EditModelVersionTagsFormButtons;
