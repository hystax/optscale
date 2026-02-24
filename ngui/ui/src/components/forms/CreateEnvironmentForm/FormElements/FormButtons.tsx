import Button from "components/Button";
import FormButtonsWrapper from "components/FormButtonsWrapper";
import SubmitButtonLoader from "components/SubmitButtonLoader";
import { useOrganizationActionRestrictions } from "hooks/useOrganizationActionRestrictions";
import { FormButtonsProps } from "../types";

const FormButtons = ({ onCancel, isLoading = false }: FormButtonsProps) => {
  const { isRestricted, restrictionReasonMessage } = useOrganizationActionRestrictions();

  return (
    <FormButtonsWrapper>
      <SubmitButtonLoader
        messageId="create"
        isLoading={isLoading}
        dataTestId="btn_create"
        loaderDataTestId="btn_create_loader"
        disabled={isRestricted}
        tooltip={{
          show: isRestricted,
          value: restrictionReasonMessage,
        }}
      />
      <Button messageId="cancel" onClick={onCancel} dataTestId="btn_cancel" />
    </FormButtonsWrapper>
  );
};

export default FormButtons;
