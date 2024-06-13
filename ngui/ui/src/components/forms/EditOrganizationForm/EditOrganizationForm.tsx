import CheckOutlinedIcon from "@mui/icons-material/CheckOutlined";
import CloseIcon from "@mui/icons-material/Close";
import Box from "@mui/material/Box";
import { useForm, FormProvider } from "react-hook-form";
import IconButton from "components/IconButton";
import { OrganizationNameField } from "./FormElements";
import { EditOrganizationFormProps, FormValues } from "./types";
import { getDefaultValues } from "./utils";

const EditOrganizationForm = ({
  currentOrganizationName,
  onSubmit,
  onCancel,
  isLoading = false
}: EditOrganizationFormProps) => {
  const methods = useForm<FormValues>({
    defaultValues: getDefaultValues({
      organizationName: currentOrganizationName
    })
  });

  const { handleSubmit } = methods;

  return (
    <FormProvider {...methods}>
      <form onSubmit={handleSubmit(onSubmit)} noValidate>
        <Box display="flex">
          <Box>
            <OrganizationNameField />
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
