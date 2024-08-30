import CheckOutlinedIcon from "@mui/icons-material/CheckOutlined";
import CloseIcon from "@mui/icons-material/Close";
import Box from "@mui/material/Box";
import { useForm, FormProvider } from "react-hook-form";
import IconButton from "components/IconButton";
import { CurrencyField } from "./FormElements";
import { EditOrganizationCurrencyFormProps, FormValues } from "./types";
import { getDefaultValues } from "./utils";

const EditOrganizationCurrencyForm = ({
  defaultCurrency,
  onSubmit,
  onCancel,
  isLoading = false
}: EditOrganizationCurrencyFormProps) => {
  const methods = useForm<FormValues>({
    defaultValues: getDefaultValues({ currency: defaultCurrency })
  });
  const { handleSubmit } = methods;

  return (
    <FormProvider {...methods}>
      <Box
        sx={{
          width: { md: "50%" }
        }}
      >
        <form onSubmit={handleSubmit(onSubmit)} noValidate>
          <Box display="flex">
            <Box flexGrow={1}>
              <CurrencyField />
            </Box>
            <Box display="flex" height="max-content">
              <IconButton isLoading={isLoading} icon={<CheckOutlinedIcon />} type="submit" />
              <IconButton icon={<CloseIcon />} onClick={onCancel} />
            </Box>
          </Box>
        </form>
      </Box>
    </FormProvider>
  );
};

export default EditOrganizationCurrencyForm;
