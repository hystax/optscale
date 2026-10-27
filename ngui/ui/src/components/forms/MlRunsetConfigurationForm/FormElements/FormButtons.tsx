import Button from "components/Button";
import FormButtonsWrapper from "components/FormButtonsWrapper";
import SubmitButtonLoader from "components/SubmitButtonLoader";
import { useOrganizationActionRestrictions } from "hooks/useOrganizationActionRestrictions";

const FormButtons = ({ onCancel, isLoading = false }) => {
  const { isRestricted, restrictionReasonMessage } = useOrganizationActionRestrictions();

  return (
    <FormButtonsWrapper>
      <SubmitButtonLoader
        variant="contained"
        color="primary"
        messageId="launch"
        type="submit"
        isLoading={isLoading}
        tooltip={{
          show: isRestricted,
          value: restrictionReasonMessage,
        }}
        disabled={isRestricted}
      />
      <Button messageId="cancel" onClick={onCancel} />
    </FormButtonsWrapper>
  );
};

export default FormButtons;
