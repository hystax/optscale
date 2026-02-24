import { Box } from "@mui/material";
import Button from "components/Button";
import ButtonLoader from "components/ButtonLoader";
import DeleteMlRunsetTemplate from "components/DeleteMlRunsetTemplate";
import FormButtonsWrapper from "components/FormButtonsWrapper";
import { useOrganizationActionRestrictions } from "hooks/useOrganizationActionRestrictions";

const FormButtons = ({ onCancel, isEdit = false, isLoading = false }) => {
  const { isRestricted, restrictionReasonMessage } = useOrganizationActionRestrictions();

  return (
    <FormButtonsWrapper justifyContent="space-between">
      <Box display="flex">
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
      </Box>
      {isEdit ? <DeleteMlRunsetTemplate /> : null}
    </FormButtonsWrapper>
  );
};

export default FormButtons;
