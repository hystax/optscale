import { FormProvider, useForm } from "react-hook-form";
import FormContentDescription from "components/FormContentDescription";
import { FormButtons, NameField } from "./FormElements";
import { FormValues, RenameDataSourceFormProps } from "./types";
import { getDefaultValues } from "./utils";

const RenameDataSourceForm = ({ name, onSubmit, onCancel, isLoading = false }: RenameDataSourceFormProps) => {
  const methods = useForm<FormValues>({
    defaultValues: getDefaultValues({
      name,
    }),
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
        <NameField />
        <FormContentDescription
          alertProps={{
            messageId: "dataSourceRenamingWarning",
          }}
        />
        <FormButtons onCancel={onCancel} isLoading={isLoading} />
      </form>
    </FormProvider>
  );
};

export default RenameDataSourceForm;
