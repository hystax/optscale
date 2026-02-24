import FormButtonsWrapper from "components/FormButtonsWrapper";
import SubmitButtonLoader from "components/SubmitButtonLoader";
import { useOrganizationActionRestrictions } from "hooks/useOrganizationActionRestrictions";

const FormButtons = ({ isLoading = false }) => {
  const { isRestricted, restrictionReasonMessage } = useOrganizationActionRestrictions();

  return (
    <FormButtonsWrapper>
      <SubmitButtonLoader
        messageId="scheduleImport"
        isLoading={isLoading}
        dataTestId="btn_confirm"
        loaderDataTestId="btn_confirm_loader"
        disabled={isRestricted}
        tooltip={{
          show: isRestricted,
          value: restrictionReasonMessage,
        }}
      />
    </FormButtonsWrapper>
  );
};

export default FormButtons;
