import { GET_POOL_OWNERS } from "api/restapi/actionTypes";
import Button from "components/Button";
import ButtonLoader from "components/ButtonLoader";
import FormButtonsWrapper from "components/FormButtonsWrapper";
import { useApiState } from "hooks/useApiState";

const AssignmentRuleFormSubmitButton = ({ isLoading = false, isEdit, onCancel }) => {
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
      />
      <Button messageId="cancel" dataTestId="btn_cancel" onClick={onCancel} />
    </FormButtonsWrapper>
  );
};

export default AssignmentRuleFormSubmitButton;
