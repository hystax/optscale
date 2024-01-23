import { Box } from "@mui/material";
import Button from "components/Button";
import ButtonLoader from "components/ButtonLoader";
import FormButtonsWrapper from "components/FormButtonsWrapper";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";

type FormButtonsProps = {
  onCancel: () => void;
  isLoading?: boolean;
};

const FormButtons = ({ onCancel, isLoading = false }: FormButtonsProps) => {
  const { isDemo } = useOrganizationInfo();

  return (
    <FormButtonsWrapper justifyContent="space-between">
      <Box display="flex">
        <ButtonLoader
          messageId="create"
          dataTestId="btn_create"
          color="primary"
          variant="contained"
          type="submit"
          disabled={isDemo}
          tooltip={{ show: isDemo, messageId: "notAvailableInLiveDemo" }}
          isLoading={isLoading}
        />
        <Button messageId="cancel" dataTestId="btn_cancel" onClick={onCancel} />
      </Box>
    </FormButtonsWrapper>
  );
};

export default FormButtons;
