import { useEffect, useMemo } from "react";
import { FormLabel } from "@mui/material";
import Skeleton from "@mui/material/Skeleton";
import { FormProvider, useForm } from "react-hook-form";
import { FormattedMessage } from "react-intl";
import KeyValueLabel from "components/KeyValueLabel";
import {
  FormButtons,
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

const MlDatasetEditForm = ({ dataset, onSubmit, onCancel, isLoadingProps = {} }) => {
  const { isGetDatasetLoading = false, isUpdateDatasetLoading = false } = isLoadingProps;

  const defaultValues = useMemo(() => getDefaultValues(dataset), [dataset]);

  const methods = useForm({
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
        data-test-id="edit_dataset_form"
        onSubmit={handleSubmit((formData) => onSubmit(prepareFormSubmissionData(formData)))}
        noValidate
      >
        {isGetDatasetLoading ? <Skeleton /> : <KeyValueLabel messageId="id" value={dataset.path} />}
        <NameField isLoading={isGetDatasetLoading} />
        <FormLabel component="p">
          <FormattedMessage id="trainingSet" />
        </FormLabel>
        <TrainingSetIdField isLoading={isGetDatasetLoading} />
        <TrainingSetTimespanFromField isLoading={isGetDatasetLoading} />
        <TrainingSetTimespanToField isLoading={isGetDatasetLoading} />
        <FormLabel component="p">
          <FormattedMessage id="validationSet" />
        </FormLabel>
        <ValidationSetIdField isLoading={isGetDatasetLoading} />
        <ValidationSetTimespanFromField isLoading={isGetDatasetLoading} />
        <ValidationSetTimespanToField isLoading={isGetDatasetLoading} />
        <DescriptionField isLoading={isGetDatasetLoading} />
        <LabelsField isLoading={isGetDatasetLoading} labels={dataset.labels} />
        <FormButtons onCancel={onCancel} isLoading={isGetDatasetLoading || isUpdateDatasetLoading} />
      </form>
    </FormProvider>
  );
};

export default MlDatasetEditForm;
