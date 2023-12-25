import { useEffect } from "react";
import { Box } from "@mui/material";
import { FormProvider, useForm } from "react-hook-form";
import {
  MlEditModelFormButtons,
  MlEditModelFormDescriptionField,
  MlEditModelFormNameField,
  MlEditModelFormOwnerField
} from "./FormElements";

const NAME_FIELD_NAME = "name";
const DESCRIPTION_FIELD_NAME = "description";
const OWNER_FIELD_NAME = "owner_id";

const MlEditModelForm = ({ model, employees, onSubmit, onCancel, isGetEmployeesLoading = false, isSubmitLoading = false }) => {
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
      [NAME_FIELD_NAME]: model.name,
      [DESCRIPTION_FIELD_NAME]: model.description,
      [OWNER_FIELD_NAME]: model.owner_id ?? ""
    });
  }, [model, reset]);

  return (
    <Box sx={{ width: { md: "50%" } }}>
      <FormProvider {...methods}>
        <form data-test-id="edit_model_form" onSubmit={handleSubmit(onSubmit)} noValidate>
          <MlEditModelFormNameField name={NAME_FIELD_NAME} />
          <MlEditModelFormDescriptionField name={DESCRIPTION_FIELD_NAME} />
          <MlEditModelFormOwnerField name={OWNER_FIELD_NAME} isLoading={isGetEmployeesLoading} employees={employees} />
          <MlEditModelFormButtons
            taskId={model.id}
            modelName={model.name}
            onCancel={onCancel}
            isLoading={isGetEmployeesLoading || isSubmitLoading}
          />
        </form>
      </FormProvider>
    </Box>
  );
};

export default MlEditModelForm;
