import Button from "components/Button";
import FormButtonsWrapper from "components/FormButtonsWrapper";
import SubmitButtonLoader from "components/SubmitButtonLoader";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";

const FormButtons = ({ isLoading, onCancel }) => {
  const { isDemo } = useOrganizationInfo();

  return (
    <FormButtonsWrapper>
      <SubmitButtonLoader
        variant="contained"
        color="primary"
        messageId="launch"
        type="submit"
        isLoading={isLoading}
        tooltip={{ show: isDemo, messageId: "notAvailableInLiveDemo" }}
        disabled={isDemo}
      />
      <Button messageId="cancel" onClick={onCancel} />
    </FormButtonsWrapper>
  );
};

export default FormButtons;
