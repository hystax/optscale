import CheckOutlinedIcon from "@mui/icons-material/CheckOutlined";
import CloseIcon from "@mui/icons-material/Close";
import Box from "@mui/material/Box";
import { useForm, FormProvider } from "react-hook-form";
import IconButton from "components/IconButton";
import WebhookUrlInput from "./Fields/WebhookUrlInput";

const WEBHOOK_URL_INPUT_NAME = "url";

const EnvironmentWebhookForm = ({ url, onSubmit, onCancel, isLoading = false }) => {
  const methods = useForm({
    defaultValues: {
      [WEBHOOK_URL_INPUT_NAME]: url
    }
  });
  const { handleSubmit } = methods;

  return (
    <FormProvider {...methods}>
      <form
        onSubmit={handleSubmit((formData) => {
          onSubmit(formData[WEBHOOK_URL_INPUT_NAME]);
        })}
        noValidate
      >
        <Box display="flex">
          <Box width="50%">
            <WebhookUrlInput name={WEBHOOK_URL_INPUT_NAME} />
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
