import { FormProvider, useForm } from "react-hook-form";
import {
  FormButtons,
  PathField,
  NameField,
  DescriptionField,
  LabelsField,
  TimespanFromField,
  TimespanToField
} from "./FormElements";
import { FormValues, MlDatasetCreateFormProps } from "./types";
import { getDefaultValues, prepareFormSubmissionData } from "./utils";

const MlDatasetCreateForm = ({ onSubmit, onCancel, isLoading = {} }: MlDatasetCreateFormProps) => {
  const { isCreateDatasetLoading = false } = isLoading;

  const methods = useForm<FormValues>({
    defaultValues: getDefaultValues()
  });

  const { handleSubmit } = methods;

  return (
    <FormProvider {...methods}>
      <form
        data-test-id="create_dataset_form"
        onSubmit={handleSubmit((formData) => onSubmit(prepareFormSubmissionData(formData)))}
        noValidate
      >
        <NameField />
        <PathField />
        <TimespanFromField />
        <TimespanToField />
        <DescriptionField />
        <LabelsField />
        <FormButtons onCancel={onCancel} isLoading={isCreateDatasetLoading} />
      </form>
    </FormProvider>
  );
};

export default MlDatasetCreateForm;
