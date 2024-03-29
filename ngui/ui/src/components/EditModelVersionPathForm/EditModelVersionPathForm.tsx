import { FormProvider, useForm } from "react-hook-form";
import { Buttons, FIELD_NAMES, PathField } from "./FormElements";
import { FormValues, EditModelVersionAliasFormProps } from "./types";

const EditModelVersionAliasForm = ({ modelVersion, onSubmit, onCancel, isLoadingProps }: EditModelVersionAliasFormProps) => {
  const { isSubmitLoading } = isLoadingProps;

  const methods = useForm<FormValues>({
    defaultValues: {
      [FIELD_NAMES.PATH_FIELD_NAME]: modelVersion.path ?? ""
    }
  });

  const { handleSubmit } = methods;

  return (
    <FormProvider {...methods}>
      <form data-test-id="version_path_form" onSubmit={handleSubmit(onSubmit)} noValidate>
        <PathField />
        <Buttons onCancel={onCancel} isLoading={isSubmitLoading} />
      </form>
    </FormProvider>
  );
};

export default EditModelVersionAliasForm;
