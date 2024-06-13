import { useEffect, useMemo } from "react";
import { FormProvider, useForm } from "react-hook-form";
import { NameField, DescriptionField, TagsFieldArray, EditFormButtons } from "./FormElements";
import { MlEditModelFormProps } from "./types";
import { getDefaultValues } from "./utils";

const MlEditModelForm = ({ model, onSubmit, onCancel, isLoadingProps = {} }: MlEditModelFormProps) => {
  const { isGetDataLoading = false, isSubmitLoading = false } = isLoadingProps;

  const defaultValues = useMemo(() => getDefaultValues(model), [model]);

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
      <form data-test-id="edit_model_form" onSubmit={handleSubmit(onSubmit)} noValidate>
        <NameField isLoading={isGetDataLoading} />
        <DescriptionField isLoading={isGetDataLoading} />
        <TagsFieldArray isLoading={isGetDataLoading} />
        <EditFormButtons modelId={model.id} modelName={model.name} onCancel={onCancel} isLoading={isSubmitLoading} />
      </form>
    </FormProvider>
  );
};

export default MlEditModelForm;
