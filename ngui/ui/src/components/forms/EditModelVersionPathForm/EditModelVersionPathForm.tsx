import { FormProvider, useForm } from "react-hook-form";
import { FromButtons, PathField } from "./FormElements";
import { FormValues, EditModelVersionPathFormProps } from "./types";
import { getDefaultValues } from "./utils";

const EditModelVersionPathForm = ({ modelVersion, onSubmit, onCancel, isLoadingProps }: EditModelVersionPathFormProps) => {
  const { isSubmitLoading } = isLoadingProps;

  const methods = useForm<FormValues>({
    defaultValues: getDefaultValues(modelVersion)
  });

  const { handleSubmit } = methods;

  return (
    <FormProvider {...methods}>
      <form data-test-id="version_path_form" onSubmit={handleSubmit(onSubmit)} noValidate>
        <PathField />
        <FromButtons onCancel={onCancel} isLoading={isSubmitLoading} />
      </form>
    </FormProvider>
  );
};

export default EditModelVersionPathForm;
