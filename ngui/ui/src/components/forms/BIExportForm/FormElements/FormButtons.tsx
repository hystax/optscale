import { Box } from "@mui/material";
import Button from "components/Button";
import ButtonLoader from "components/ButtonLoader";
import DeleteBIExport from "components/DeleteBIExport";
import FormButtonsWrapper from "components/FormButtonsWrapper";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";

const FormButtons = ({ onCancel, isEdit = false, isLoading = false }) => {
  const { isDemo } = useOrganizationInfo();

  return (
    <FormButtonsWrapper justifyContent="space-between">
      <Box display="flex">
        <ButtonLoader
          messageId={isEdit ? "save" : "create"}
          dataTestId="btn_save"
          color="primary"
          variant="contained"
          type="submit"
          disabled={isDemo}
          isLoading={isLoading}
        />
        <Button messageId="cancel" dataTestId="btn_cancel" onClick={onCancel} />
      </Box>
      {isEdit ? <DeleteBIExport /> : null}
    </FormButtonsWrapper>
  );
};

export default FormButtons;
