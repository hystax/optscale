import Button from "components/Button";
import ButtonLoader from "components/ButtonLoader";
import FormButtonsWrapper from "components/FormButtonsWrapper";
import { useOrganizationActionRestrictions } from "hooks/useOrganizationActionRestrictions";
import { FormButtonsProps } from "../types";

const FormButtons = ({ onCancel, isLoading = false }: FormButtonsProps) => {
  const { isRestricted, restrictionReasonMessage } = useOrganizationActionRestrictions();

  return (
    <FormButtonsWrapper>
      <ButtonLoader
        isLoading={isLoading}
        variant="contained"
        color="primary"
        messageId="save"
        type="submit"
        loaderDataTestId="loading_btn_save"
        dataTestId="btn_save"
        disabled={isRestricted}
        tooltip={{
          show: isRestricted,
          value: restrictionReasonMessage,
        }}
      />
      <Button messageId="cancel" dataTestId="btn_cancel" onClick={onCancel} />
    </FormButtonsWrapper>
  );
};

export default FormButtons;
