import { useEffect } from "react";
import { Box } from "@mui/material";
import { FormProvider, useForm } from "react-hook-form";
import { OwnerField, FormButtons, DescriptionField, NameField } from "./FormElements";

const NAME_FIELD_NAME = "name";
const DESCRIPTION_FIELD_NAME = "description";
const OWNER_FIELD_NAME = "owner_id";

const MlEditTaskForm = ({ task, employees, onSubmit, onCancel, isGetEmployeesLoading = false, isSubmitLoading = false }) => {
  const methods = useForm({
    defaultValues: {
      [NAME_FIELD_NAME]: "",
      [DESCRIPTION_FIELD_NAME]: "",
      [OWNER_FIELD_NAME]: ""
    }
  });

  const { reset, handleSubmit } = methods;

  useEffect(() => {
    reset({
      [NAME_FIELD_NAME]: task.name,
      [DESCRIPTION_FIELD_NAME]: task.description,
      [OWNER_FIELD_NAME]: task.owner_id ?? ""
    });
  }, [task, reset]);

  return (
    <Box sx={{ width: { md: "50%" } }}>
      <FormProvider {...methods}>
        <form data-test-id="edit_task_form" onSubmit={handleSubmit(onSubmit)} noValidate>
          <NameField name={NAME_FIELD_NAME} />
          <DescriptionField name={DESCRIPTION_FIELD_NAME} />
          <OwnerField name={OWNER_FIELD_NAME} isLoading={isGetEmployeesLoading} employees={employees} />
          <FormButtons
            taskId={task.id}
            taskName={task.name}
            onCancel={onCancel}
            isLoading={isGetEmployeesLoading || isSubmitLoading}
          />
        </form>
      </FormProvider>
    </Box>
  );
};

export default MlEditTaskForm;
