import { FormProvider, useForm } from "react-hook-form";
import { FormButtons, NameField, DescriptionField, PathField, TagsFieldArray } from "./FormElements";
import { FormValues, MlCreateArtifactFormProps } from "./types";
import { getDefaultValues, prepareFormSubmissionData } from "./utils";

const MlCreateArtifactForm = ({ onSubmit, onCancel, isLoadingProps = {} }: MlCreateArtifactFormProps) => {
  const { isCreateArtifactLoading = false } = isLoadingProps;

  const methods = useForm<FormValues>({
    defaultValues: getDefaultValues()
  });

  const { handleSubmit } = methods;

  return (
    <FormProvider {...methods}>
      <form
        data-test-id="create_artifact_form"
        onSubmit={handleSubmit((formData) => onSubmit(prepareFormSubmissionData(formData)))}
        noValidate
      >
        <NameField />
        <PathField />
        <DescriptionField />
        <TagsFieldArray />
        <FormButtons onCancel={onCancel} isLoading={isCreateArtifactLoading} />
      </form>
    </FormProvider>
  );
};

export default MlCreateArtifactForm;
