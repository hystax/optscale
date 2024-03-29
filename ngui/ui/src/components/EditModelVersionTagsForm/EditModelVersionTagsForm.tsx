import { FormProvider, useForm } from "react-hook-form";
import { Buttons, TagsFieldArray } from "./FormElements";
import { EditModelVersionAliasFormProps, FormValues } from "./types";
import { getDefaultValues } from "./utils";

const EditModelVersionTagsForm = ({ tags, onSubmit, onCancel, isLoadingProps }: EditModelVersionAliasFormProps) => {
  const { isSubmitLoading = false } = isLoadingProps;

  const methods = useForm<FormValues>({
    defaultValues: getDefaultValues(tags)
  });

  const { handleSubmit } = methods;

  return (
    <FormProvider {...methods}>
      <form data-test-id="version_tags_form" onSubmit={handleSubmit(onSubmit)} noValidate>
        <TagsFieldArray />
        <Buttons isLoading={isSubmitLoading} onCancel={onCancel} />
      </form>
    </FormProvider>
  );
};

export default EditModelVersionTagsForm;
