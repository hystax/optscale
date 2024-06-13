import { FormProvider, useForm } from "react-hook-form";
import { FormButtons, NameField, MetricsField, KeyField, OwnerField, DescriptionField } from "./FormElements";
import { FormValues } from "./types";
import { getDefaultValues } from "./utils";

const MlTaskCreateForm = ({ onSubmit, onCancel, employees = [], metrics, isLoading = {} }) => {
  const { isGetEmployeesLoading = false, isCreateTaskLoading = false, isGetGlobalMetricsLoading = false } = isLoading;

  const methods = useForm<FormValues>({
    defaultValues: getDefaultValues()
  });

  const { handleSubmit } = methods;

  return (
    <FormProvider {...methods}>
      <form data-test-id="create_task_form" onSubmit={handleSubmit(onSubmit)} noValidate>
        <NameField />
        <DescriptionField />
        <KeyField />
        <OwnerField employees={employees} isLoading={isGetEmployeesLoading} />
        <MetricsField metrics={metrics} isLoading={isGetGlobalMetricsLoading} />
        <FormButtons
          onCancel={onCancel}
          isLoading={isGetEmployeesLoading || isCreateTaskLoading || isGetGlobalMetricsLoading}
        />
      </form>
    </FormProvider>
  );
};

export default MlTaskCreateForm;
