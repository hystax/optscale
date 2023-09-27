import React, { useEffect } from "react";
import { FormProvider, useForm } from "react-hook-form";
import { CriticalInput, FormButtons, RequiringAttentionInput, FIELD_NAMES } from "./FormElements";

const S3DuplicateFinderSettingsForm = ({ requiringAttention, critical, onCancel, onSubmit, isLoadingProps = {} }) => {
  const { isGetDataLoading = false, isSubmitLoading = false } = isLoadingProps;

  const methods = useForm({
    defaultValues: {
      [FIELD_NAMES.REQUIRING_ATTENTION_FIELD_NAME]: "",
      [FIELD_NAMES.CRITICAL_FIELD_NAME]: ""
    }
  });

  const { handleSubmit, reset } = methods;

  useEffect(() => {
    reset((formValues) => ({
      ...formValues,
      [FIELD_NAMES.REQUIRING_ATTENTION_FIELD_NAME]: requiringAttention.toString(),
      [FIELD_NAMES.CRITICAL_FIELD_NAME]: critical.toString()
    }));
  }, [critical, requiringAttention, reset]);

  return (
    <FormProvider {...methods}>
      <form
        onSubmit={handleSubmit((formData) =>
          onSubmit({
            thresholds: {
              requiring_attention: Number(formData[FIELD_NAMES.REQUIRING_ATTENTION_FIELD_NAME]),
              critical: Number(formData[FIELD_NAMES.CRITICAL_FIELD_NAME])
            }
          })
        )}
        noValidate
      >
        <RequiringAttentionInput isLoading={isGetDataLoading} />
        <CriticalInput isLoading={isGetDataLoading} />
        <FormButtons isLoading={isGetDataLoading || isSubmitLoading} onCancel={onCancel} />
      </form>
    </FormProvider>
  );
};

export default S3DuplicateFinderSettingsForm;
