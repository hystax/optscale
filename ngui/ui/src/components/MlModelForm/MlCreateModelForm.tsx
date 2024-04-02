import { FormProvider, useForm } from "react-hook-form";
import { NameField, KeyField, DescriptionField, TagsFieldArray, CreateFormButtons } from "./FormElements";
import { FormValues, MlCreateModelFormProps } from "./types";
import { getDefaultValues } from "./utils";

const MlCreateModelForm = ({ onSubmit, onCancel, isLoadingProps = {} }: MlCreateModelFormProps) => {
  const { isSubmitLoading = false } = isLoadingProps;

  const methods = useForm<FormValues>({
    defaultValues: getDefaultValues()
  });

  const { handleSubmit } = methods;

  return (
    <FormProvider {...methods}>
      <form data-test-id="create_model_form" onSubmit={handleSubmit(onSubmit)} noValidate>
        <NameField />
        <KeyField />
        <DescriptionField />
        <TagsFieldArray />
        <CreateFormButtons isLoading={isSubmitLoading} onCancel={onCancel} />
      </form>
    </FormProvider>
  );
};

export default MlCreateModelForm;
