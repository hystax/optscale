import { Stack } from "@mui/material";
import { FormProvider, useForm } from "react-hook-form";
import InlineSeverityAlert from "components/InlineSeverityAlert";
import { SPACING_1 } from "utils/layouts";
import { FormButtons, NameField } from "./FormElements";
import { FormValues, RenameDataSourceFormProps } from "./types";
import { getDefaultValues } from "./utils";

const RenameDataSourceForm = ({ name, onSubmit, onCancel, isLoading = false }: RenameDataSourceFormProps) => {
  const methods = useForm<FormValues>({
    defaultValues: getDefaultValues({
      name
    })
  });

  const { handleSubmit } = methods;

  return (
    <FormProvider {...methods}>
      <form
        onSubmit={handleSubmit(async (formData) => {
          onSubmit(formData);
        })}
        noValidate
      >
        <Stack spacing={SPACING_1}>
          <div>
            <NameField />
          </div>
          <div>
            <InlineSeverityAlert messageId="dataSourceRenamingWarning" />
          </div>
        </Stack>
        <FormButtons onCancel={onCancel} isLoading={isLoading} />
      </form>
    </FormProvider>
  );
};

export default RenameDataSourceForm;
