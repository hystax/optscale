import { FormProvider, useForm } from "react-hook-form";
import { FormButtons, NameField, MetricsField, KeyField, OwnerField, DescriptionField } from "./FormElements";

const NAME_FIELD_NAME = "name";
const DESCRIPTION_FIELD_NAME = "description";
const KEY_FIELD_NAME = "key";
const OWNER_FIELD_NAME = "owner_id";
const METRICS_FIELD_NAME = "metrics";

const MlTaskCreateForm = ({ onSubmit, onCancel, employees = [], metrics, isLoading = {} }) => {
  const { isGetEmployeesLoading = false, isCreateTaskLoading = false, isGetGlobalMetricsLoading = false } = isLoading;

  const methods = useForm({
    defaultValues: {
      [NAME_FIELD_NAME]: "",
      [DESCRIPTION_FIELD_NAME]: "",
      [KEY_FIELD_NAME]: "",
      [OWNER_FIELD_NAME]: "",
      [METRICS_FIELD_NAME]: []
    }
  });

  const { handleSubmit } = methods;

  return (
    <FormProvider {...methods}>
      <form data-test-id="create_task_form" onSubmit={handleSubmit(onSubmit)} noValidate>
        <NameField name={NAME_FIELD_NAME} />
        <DescriptionField name={DESCRIPTION_FIELD_NAME} />
        <KeyField name={KEY_FIELD_NAME} />
        <OwnerField name={OWNER_FIELD_NAME} employees={employees} isLoading={isGetEmployeesLoading} />
        <MetricsField name={METRICS_FIELD_NAME} metrics={metrics} isLoading={isGetGlobalMetricsLoading} />
        <FormButtons
          onCancel={onCancel}
          isLoading={isGetEmployeesLoading || isCreateTaskLoading || isGetGlobalMetricsLoading}
        />
      </form>
    </FormProvider>
  );
};

export default MlTaskCreateForm;
