import React, { useEffect } from "react";
import { Box } from "@mui/material";
import PropTypes from "prop-types";
import { FormProvider, useForm } from "react-hook-form";
import { MlEditApplicationFormButtons, MlEditApplicationFormNameField, MlEditApplicationFormOwnerField } from "./FormElements";

const NAME_FIELD_NAME = "name";
const OWNER_FIELD_NAME = "ownerId";

const MlEditApplicationForm = ({
  application,
  employees,
  onSubmit,
  onCancel,
  isGetEmployeesLoading = false,
  isSubmitLoading = false
}) => {
  const methods = useForm({
    defaultValues: {
      [NAME_FIELD_NAME]: "",
      [OWNER_FIELD_NAME]: ""
    }
  });

  const { reset, handleSubmit } = methods;

  useEffect(() => {
    reset({
      [NAME_FIELD_NAME]: application.name,
      [OWNER_FIELD_NAME]: application.owner_id ?? ""
    });
  }, [application, reset]);

  return (
    <Box sx={{ width: { md: "50%" } }}>
      <FormProvider {...methods}>
        <form
          data-test-id="create_application_form"
          onSubmit={handleSubmit((formData) =>
            onSubmit({
              name: formData[NAME_FIELD_NAME],
              ownerId: formData[OWNER_FIELD_NAME]
            })
          )}
          noValidate
        >
          <MlEditApplicationFormNameField name={NAME_FIELD_NAME} />
          <MlEditApplicationFormOwnerField name={OWNER_FIELD_NAME} isLoading={isGetEmployeesLoading} employees={employees} />
          <MlEditApplicationFormButtons
            applicationId={application.id}
            applicationName={application.name}
            onCancel={onCancel}
            isLoading={isGetEmployeesLoading || isSubmitLoading}
          />
        </form>
      </FormProvider>
    </Box>
  );
};

MlEditApplicationForm.propTypes = {
  onSubmit: PropTypes.func.isRequired,
  application: PropTypes.object.isRequired,
  employees: PropTypes.array.isRequired,
  onCancel: PropTypes.func.isRequired,
  isGetEmployeesLoading: PropTypes.bool,
  isSubmitLoading: PropTypes.bool
};

export default MlEditApplicationForm;
