import { Box } from "@mui/material";
import Button from "components/Button";
import ButtonLoader from "components/ButtonLoader";
import FormButtonsWrapper from "components/FormButtonsWrapper";
import { useOrganizationActionRestrictions } from "hooks/useOrganizationActionRestrictions";

type FormButtonsProps = {
  submitButtonMessageId: string;
  onCancel: () => void;
  isLoading?: boolean;
};

const FormButtons = ({ submitButtonMessageId, onCancel, isLoading = false }: FormButtonsProps) => {
  const { isRestricted, restrictionReasonMessage } = useOrganizationActionRestrictions();

  return (
    <FormButtonsWrapper justifyContent="space-between">
      <Box display="flex">
        <ButtonLoader
          messageId={submitButtonMessageId}
          dataTestId="btn_create"
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
    </FormButtonsWrapper>
  );
};

export default FormButtons;
