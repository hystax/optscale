import Button from "components/Button";
import ButtonLoader from "components/ButtonLoader";
import FormButtonsWrapper from "components/FormButtonsWrapper";
import { useOrganizationActionRestrictions } from "hooks/useOrganizationActionRestrictions";
import { FormButtonsProps } from "../types";

const FormButtons = ({ onCancel, onReset, isResetDisabled, isLoading }: FormButtonsProps) => {
  const { isRestricted, restrictionReasonMessage } = useOrganizationActionRestrictions();

  return (
    <FormButtonsWrapper>
      <ButtonLoader
        dataTestId="btn_save_focus_mapping"
        loaderDataTestId="loading_btn_save_focus_mapping"
        messageId="save"
        color="primary"
        variant="contained"
        type="submit"
        disabled={isRestricted || isLoading}
        tooltip={{
          show: isRestricted,
          value: restrictionReasonMessage,
        }}
        isLoading={isLoading}
      />
      <Button
        dataTestId="btn_reset_focus_mapping"
        messageId="resetToDefaults"
        variant="outlined"
        onClick={onReset}
        disabled={isResetDisabled || isLoading}
      />
      <Button dataTestId="btn_cancel_edit_focus_mapping" messageId="cancel" onClick={onCancel} />
    </FormButtonsWrapper>
  );
};

export default FormButtons;
