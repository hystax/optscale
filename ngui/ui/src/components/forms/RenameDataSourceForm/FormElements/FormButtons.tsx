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
        dataTestId="btn_rename_data_source"
        loaderDataTestId="loading_btn_rename_data_source"
        messageId="save"
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
      <Button dataTestId="btn_cancel_rename_data_source" messageId="cancel" onClick={onCancel} />
    </FormButtonsWrapper>
  );
};

export default FormButtons;
