import Button from "components/Button";
import ButtonLoader from "components/ButtonLoader";
import FormButtonsWrapper from "components/FormButtonsWrapper";
import { useOrganizationActionRestrictions } from "hooks/useOrganizationActionRestrictions";

const FormButtons = ({ onCancel, isLoading = false }) => {
  const { isRestricted, restrictionReasonMessage } = useOrganizationActionRestrictions();

  return (
    <FormButtonsWrapper>
      <ButtonLoader
        messageId="save"
        dataTestId="btn_save"
        color="primary"
        variant="contained"
        type="submit"
        disabled={isRestricted}
        tooltip={{
          show: isRestricted,
          value: restrictionReasonMessage,
        }}
        isLoading={isLoading}
      />
      <Button messageId="cancel" dataTestId="btn_cancel" onClick={onCancel} />
    </FormButtonsWrapper>
  );
};

export default FormButtons;
