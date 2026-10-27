import Button from "components/Button";
import ButtonLoader from "components/ButtonLoader";
import FormButtonsWrapper from "components/FormButtonsWrapper";
import { useOrganizationActionRestrictions } from "hooks/useOrganizationActionRestrictions";

const FormButtons = ({ isLoading, onCancel }) => {
  const { isRestricted, restrictionReasonMessage } = useOrganizationActionRestrictions();

  return (
    <FormButtonsWrapper>
      <ButtonLoader
        dataTestId="bnt_add"
        isLoading={isLoading}
        variant="contained"
        color="primary"
        messageId="book"
        type="submit"
        disabled={isRestricted}
        tooltip={{
          show: isRestricted,
          value: restrictionReasonMessage,
        }}
      />
      <Button dataTestId="bnt_cancel" messageId="cancel" variant="outlined" onClick={onCancel} />
    </FormButtonsWrapper>
  );
};

export default FormButtons;
