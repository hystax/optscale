import CheckOutlinedIcon from "@mui/icons-material/CheckOutlined";
import CloseIcon from "@mui/icons-material/Close";
import Box from "@mui/material/Box";
import { useForm, FormProvider } from "react-hook-form";
import IconButton from "components/IconButton";
import OrganizationNameInput from "./Fields/OrganizationNameInput";

const ORGANIZATION_NAME_INPUT_NAME = "organizationName";

const EditOrganizationForm = ({ currentOrganizationName, onSubmit, onCancel, isLoading = false }) => {
  const methods = useForm({
    defaultValues: {
      [ORGANIZATION_NAME_INPUT_NAME]: currentOrganizationName
    }
  });
  const { handleSubmit } = methods;

  return (
    <FormProvider {...methods}>
      <form
        onSubmit={handleSubmit((formData) => {
          onSubmit(formData[ORGANIZATION_NAME_INPUT_NAME]);
        })}
        noValidate
      >
        <Box display="flex">
          <Box>
            <OrganizationNameInput name={ORGANIZATION_NAME_INPUT_NAME} />
          </Box>
          <Box display="flex" height="max-content">
            <IconButton isLoading={isLoading} icon={<CheckOutlinedIcon />} type="submit" />
            <IconButton icon={<CloseIcon />} onClick={onCancel} />
          </Box>
        </Box>
      </form>
    </FormProvider>
  );
};

export default EditOrganizationForm;
