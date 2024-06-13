import { useEffect } from "react";
import { FormProvider, useForm } from "react-hook-form";
import { CriticalField, FormButtons, RequiringAttentionField } from "./FormElements";
import { FormValues, S3DuplicateFinderSettingsFormProps } from "./types";
import { getDefaultValues } from "./utils";

const S3DuplicateFinderSettingsForm = ({
  requiringAttention,
  critical,
  onCancel,
  onSubmit,
  isLoadingProps = {}
}: S3DuplicateFinderSettingsFormProps) => {
  const { isGetDataLoading = false, isSubmitLoading = false } = isLoadingProps;

  const methods = useForm<FormValues>({
    defaultValues: getDefaultValues()
  });

  const { handleSubmit, reset } = methods;

  useEffect(() => {
    reset((formValues) => ({
      ...formValues,
      ...getDefaultValues({
        requiringAttention,
        critical
      })
    }));
  }, [critical, requiringAttention, reset]);

  return (
    <FormProvider {...methods}>
      <form onSubmit={handleSubmit(onSubmit)} noValidate>
        <RequiringAttentionField isLoading={isGetDataLoading} />
        <CriticalField isLoading={isGetDataLoading} />
        <FormButtons isLoading={isGetDataLoading || isSubmitLoading} onCancel={onCancel} />
      </form>
    </FormProvider>
  );
};

export default S3DuplicateFinderSettingsForm;
