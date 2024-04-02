import { FormLabel } from "@mui/material";
import { FormProvider, useForm } from "react-hook-form";
import { FormattedMessage } from "react-intl";
import {
  FormButtons,
  IdField,
  NameField,
  DescriptionField,
  LabelsField,
  TrainingSetIdField,
  ValidationSetIdField,
  TrainingSetTimespanFromField,
  TrainingSetTimespanToField,
  ValidationSetTimespanFromField,
  ValidationSetTimespanToField
} from "./FormElements";
import { getDefaultValues, prepareFormSubmissionData } from "./utils";

const MlDatasetCreateForm = ({ onSubmit, onCancel, isLoading = {} }) => {
  const { isCreateDatasetLoading = false } = isLoading;

  const methods = useForm({
    defaultValues: getDefaultValues()
  });

  const { handleSubmit } = methods;

  return (
    <FormProvider {...methods}>
      <form
        data-test-id="create_task_form"
        onSubmit={handleSubmit((formData) => onSubmit(prepareFormSubmissionData(formData)))}
        noValidate
      >
        <IdField autoFocus />
        <NameField />
        <FormLabel component="p">
          <FormattedMessage id="trainingSet" />
        </FormLabel>
        <TrainingSetIdField />
        <TrainingSetTimespanFromField />
        <TrainingSetTimespanToField />
        <FormLabel component="p">
          <FormattedMessage id="validationSet" />
        </FormLabel>
        <ValidationSetIdField />
        <ValidationSetTimespanFromField />
        <ValidationSetTimespanToField />
        <DescriptionField />
        <LabelsField />
        <FormButtons onCancel={onCancel} isLoading={isCreateDatasetLoading} />
      </form>
    </FormProvider>
  );
};

export default MlDatasetCreateForm;
