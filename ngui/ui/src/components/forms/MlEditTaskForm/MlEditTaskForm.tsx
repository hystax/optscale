import { useEffect } from "react";
import { Box } from "@mui/material";
import { FormProvider, useForm } from "react-hook-form";
import { OwnerField, FormButtons, DescriptionField, NameField } from "./FormElements";
import { FormValues } from "./types";
import { getDefaultValues } from "./utils";

const MlEditTaskForm = ({ task, employees, onSubmit, onCancel, isGetEmployeesLoading = false, isSubmitLoading = false }) => {
  const methods = useForm<FormValues>({
    defaultValues: getDefaultValues()
  });

  const { reset, handleSubmit } = methods;

  useEffect(() => {
    reset(getDefaultValues(task));
  }, [task, reset]);

  return (
    <Box sx={{ width: { md: "50%" } }}>
      <FormProvider {...methods}>
        <form data-test-id="edit_task_form" onSubmit={handleSubmit(onSubmit)} noValidate>
          <NameField />
          <DescriptionField />
          <OwnerField isLoading={isGetEmployeesLoading} employees={employees} />
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
