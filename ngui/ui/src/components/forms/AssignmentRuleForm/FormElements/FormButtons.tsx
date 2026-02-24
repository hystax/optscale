import { GET_POOL_OWNERS } from "api/restapi/actionTypes";
import Button from "components/Button";
import ButtonLoader from "components/ButtonLoader";
import FormButtonsWrapper from "components/FormButtonsWrapper";
import { useApiState } from "hooks/useApiState";
import { useOrganizationActionRestrictions } from "hooks/useOrganizationActionRestrictions";
import { FormButtonsProps } from "../types";

const FormButtons = ({ isLoading = false, isEdit, onCancel }: FormButtonsProps) => {
  const { isRestricted, restrictionReasonMessage } = useOrganizationActionRestrictions();

  const { isLoading: isGetPoolOwnerLoading } = useApiState(GET_POOL_OWNERS);

  return (
    <FormButtonsWrapper>
      <ButtonLoader
        messageId={isEdit ? "save" : "create"}
        dataTestId={isEdit ? "btn_save" : "btn_create"}
        color="primary"
        variant="contained"
        type="submit"
        isLoading={isLoading || isGetPoolOwnerLoading}
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
