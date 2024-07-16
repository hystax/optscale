import { useEffect, useMemo } from "react";
import { FormProvider, useForm } from "react-hook-form";
import { FormButtons, NameField, DescriptionField, LabelsField, TimespanFromField, TimespanToField } from "./FormElements";
import { FormValues, MlDatasetEditFormProps } from "./types";
import { getDefaultValues, prepareFormSubmissionData } from "./utils";

const MlDatasetEditForm = ({ dataset, onSubmit, onCancel, isLoadingProps = {} }: MlDatasetEditFormProps) => {
  const { isGetDatasetLoading = false, isUpdateDatasetLoading = false } = isLoadingProps;

  const defaultValues = useMemo(() => getDefaultValues(dataset), [dataset]);

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
        data-test-id="edit_dataset_form"
        onSubmit={handleSubmit((formData) => onSubmit(prepareFormSubmissionData(formData)))}
        noValidate
      >
        <NameField isLoading={isGetDatasetLoading} />
        <TimespanFromField isLoading={isGetDatasetLoading} />
        <TimespanToField isLoading={isGetDatasetLoading} />
        <DescriptionField isLoading={isGetDatasetLoading} />
        <LabelsField isLoading={isGetDatasetLoading} labels={dataset.labels} />
        <FormButtons onCancel={onCancel} isLoading={isGetDatasetLoading || isUpdateDatasetLoading} />
      </form>
    </FormProvider>
  );
};

export default MlDatasetEditForm;
