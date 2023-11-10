import { useEffect } from "react";
import { Box } from "@mui/material";
import { FormProvider, useForm } from "react-hook-form";
import { MlEditModelFormButtons, MlEditModelFormNameField, MlEditModelFormOwnerField } from "./FormElements";

const NAME_FIELD_NAME = "name";
const OWNER_FIELD_NAME = "ownerId";

const MlEditModelForm = ({ model, employees, onSubmit, onCancel, isGetEmployeesLoading = false, isSubmitLoading = false }) => {
  const methods = useForm({
    defaultValues: {
      [NAME_FIELD_NAME]: "",
      [OWNER_FIELD_NAME]: ""
    }
  });

  const { reset, handleSubmit } = methods;

  useEffect(() => {
    reset({
      [NAME_FIELD_NAME]: model.name,
      [OWNER_FIELD_NAME]: model.owner_id ?? ""
    });
  }, [model, reset]);

  return (
    <Box sx={{ width: { md: "50%" } }}>
      <FormProvider {...methods}>
        <form
          data-test-id="edit_model_form"
          onSubmit={handleSubmit((formData) =>
            onSubmit({
              name: formData[NAME_FIELD_NAME],
              ownerId: formData[OWNER_FIELD_NAME]
            })
          )}
          noValidate
        >
          <MlEditModelFormNameField name={NAME_FIELD_NAME} />
          <MlEditModelFormOwnerField name={OWNER_FIELD_NAME} isLoading={isGetEmployeesLoading} employees={employees} />
          <MlEditModelFormButtons
            modelId={model.id}
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
