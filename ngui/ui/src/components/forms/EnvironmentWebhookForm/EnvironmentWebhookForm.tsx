import CheckOutlinedIcon from "@mui/icons-material/CheckOutlined";
import CloseIcon from "@mui/icons-material/Close";
import Box from "@mui/material/Box";
import { useForm, FormProvider } from "react-hook-form";
import IconButton from "components/IconButton";
import WebhookUrlField from "./FormElements/WebhookUrlField";
import { EnvironmentWebhookFormProps, FormValues } from "./types";
import { getDefaultValues } from "./utils";

const EnvironmentWebhookForm = ({ url, onSubmit, onCancel, isLoading = false }: EnvironmentWebhookFormProps) => {
  const methods = useForm<FormValues>({
    defaultValues: getDefaultValues({
      url
    })
  });

  const { handleSubmit } = methods;

  return (
    <FormProvider {...methods}>
      <form
        onSubmit={handleSubmit((formData) => {
          onSubmit(formData.url);
        })}
        noValidate
      >
        <Box display="flex">
          <Box width="50%">
            <WebhookUrlField />
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

export default EnvironmentWebhookForm;
