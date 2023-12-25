import { Box } from "@mui/material";
import Button from "components/Button";
import ButtonLoader from "components/ButtonLoader";
import FormButtonsWrapper from "components/FormButtonsWrapper";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";

const FormButtons = ({ onCancel, isLoading = false }) => {
  const { isDemo } = useOrganizationInfo();

  return (
    <FormButtonsWrapper mt={2} mb={2} justifyContent="space-between">
      <Box display="flex">
        <ButtonLoader
          messageId={"save"}
          dataTestId="btn_save"
          color="primary"
          variant="contained"
          type="submit"
          disabled={isDemo}
          isLoading={isLoading}
        />
        <Button messageId="cancel" dataTestId="btn_cancel" onClick={onCancel} />
      </Box>
    </FormButtonsWrapper>
  );
};

export default FormButtons;
