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
        messageId="save"
        type="submit"
        isLoading={isLoading}
        disabled={isRestricted}
        tooltip={{
          show: isRestricted,
          value: restrictionReasonMessage,
        }}
      />
      <Button messageId="cancel" onClick={onCancel} />
    </FormButtonsWrapper>
  );
};

export default FormButtons;
