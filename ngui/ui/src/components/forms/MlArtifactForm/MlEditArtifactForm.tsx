import { useEffect, useMemo } from "react";
import { FormProvider, useForm } from "react-hook-form";
import { FormButtons, NameField, DescriptionField, PathField, TagsFieldArray } from "./FormElements";
import { FormValues, MlEditArtifactFormProps } from "./types";
import { getDefaultValues, prepareFormSubmissionData } from "./utils";

const MlEditArtifactForm = ({ artifact, onSubmit, onCancel, isLoadingProps = {} }: MlEditArtifactFormProps) => {
  const { isGetArtifactLoading = false, isUpdateArtifactLoading = false } = isLoadingProps;

  const defaultValues = useMemo(() => getDefaultValues(artifact), [artifact]);

  const methods = useForm<FormValues>({
    defaultValues
  });

  const { handleSubmit, reset } = methods;

  useEffect(() => {
    reset((formValues) => ({
      ...formValues,
      ...defaultValues
    }));
  }, [defaultValues, reset]);

  return (
    <FormProvider {...methods}>
      <form
        data-test-id="edit_artifact_form"
        onSubmit={handleSubmit((formData) => onSubmit(prepareFormSubmissionData(formData)))}
        noValidate
      >
        <NameField isLoading={isGetArtifactLoading} />
        <PathField isLoading={isGetArtifactLoading} />
        <DescriptionField isLoading={isGetArtifactLoading} />
        <TagsFieldArray isLoading={isGetArtifactLoading} />
        <FormButtons onCancel={onCancel} isLoading={isGetArtifactLoading || isUpdateArtifactLoading} />
      </form>
    </FormProvider>
  );
};

export default MlEditArtifactForm;
