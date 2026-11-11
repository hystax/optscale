import { FormProvider, useForm } from "react-hook-form";
import FocusMappingEditor, {
  FOCUS_MAPPING_FIELD_NAME,
  MAPPING_FIELDS,
  getDefaultFocusMappingFormValues,
  isEmptyApiMapping,
  mappingApiToFormValues,
  mappingFormValuesToApi,
} from "components/FocusMappingEditor";
import FormContentDescription from "components/FormContentDescription";
import { FormButtons } from "./FormElements";
import { EditFocusMappingFormProps, FormValues } from "./types";

const EditFocusMappingForm = ({ mapping, onSubmit, onCancel, isLoading = false }: EditFocusMappingFormProps) => {
  const methods = useForm<FormValues>({
    defaultValues: {
      [FOCUS_MAPPING_FIELD_NAME]: mappingApiToFormValues(mapping),
    },
  });

  const { handleSubmit, reset, watch } = methods;

  // Only customized fields are sent, so the mapping is empty when no field is customized
  const isEveryFieldDefault = !watch(
    MAPPING_FIELDS.map(({ key }) => `${FOCUS_MAPPING_FIELD_NAME}.${key}.enabled` as const)
  ).some(Boolean);

  return (
    <FormProvider {...methods}>
      <form
        onSubmit={handleSubmit((formData) => {
          const newMapping = mappingFormValuesToApi(formData[FOCUS_MAPPING_FIELD_NAME]);
          // A mapping with every field on defaults is a reset
          onSubmit(isEmptyApiMapping(newMapping) ? null : newMapping);
        })}
        noValidate
      >
        <FormContentDescription
          fullWidth
          alertProps={{
            messageId: "focusMappingChangeWarning",
            severity: "warning",
          }}
        />
        <FocusMappingEditor name={FOCUS_MAPPING_FIELD_NAME} showTitle={false} />
        <FormButtons
          onCancel={onCancel}
          // Only sets every field to default, the mapping is sent on save
          onReset={() => reset({ [FOCUS_MAPPING_FIELD_NAME]: getDefaultFocusMappingFormValues() }, { keepDefaultValues: true })}
          isResetDisabled={isEveryFieldDefault}
          isLoading={isLoading}
        />
      </form>
    </FormProvider>
  );
};

export default EditFocusMappingForm;
