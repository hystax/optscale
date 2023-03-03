import React from "react";
import PropTypes from "prop-types";
import { FormProvider, useForm } from "react-hook-form";
import {
  MlModelCreateFormButtons,
  MlModelCreateFormKeyField,
  MlModelCreateFormNameField,
  MlModelCreateFormOwnerField,
  MlModelCreateFormParametersField
} from "./FormElements";

const NAME_FIELD_NAME = "name";
const KEY_FIELD_NAME = "key";
const OWNER_FIELD_NAME = "owner_id";
const GOALS_FIELD_NAME = "goals";

const MlModelCreateForm = ({ onSubmit, onCancel, employees = [], parameters, isLoading = {} }) => {
  const { isGetEmployeesLoading = false, isCreateApplicationLoading = false, isGetGlobalParametersLoading = false } = isLoading;

  const methods = useForm({
    defaultValues: {
      [NAME_FIELD_NAME]: "",
      [KEY_FIELD_NAME]: "",
      [OWNER_FIELD_NAME]: "",
      [GOALS_FIELD_NAME]: []
    }
  });

  const { handleSubmit } = methods;

  return (
    <FormProvider {...methods}>
      <form data-test-id="create_application_form" onSubmit={handleSubmit(onSubmit)} noValidate>
        <MlModelCreateFormNameField name={NAME_FIELD_NAME} />
        <MlModelCreateFormKeyField name={KEY_FIELD_NAME} />
        <MlModelCreateFormOwnerField name={OWNER_FIELD_NAME} employees={employees} isLoading={isGetEmployeesLoading} />
        <MlModelCreateFormParametersField
          name={GOALS_FIELD_NAME}
          parameters={parameters}
          isLoading={isGetGlobalParametersLoading}
        />
        <MlModelCreateFormButtons
          onCancel={onCancel}
          isLoading={isGetEmployeesLoading || isCreateApplicationLoading || isGetGlobalParametersLoading}
        />
      </form>
    </FormProvider>
  );
};

MlModelCreateForm.propTypes = {
  onSubmit: PropTypes.func.isRequired,
  onCancel: PropTypes.func.isRequired,
  employees: PropTypes.array,
  parameters: PropTypes.array,
  isLoading: PropTypes.shape({
    isGetEmployeesLoading: PropTypes.bool,
    isCreateApplicationLoading: PropTypes.bool,
    isGetGlobalParametersLoading: PropTypes.bool
  })
};

export default MlModelCreateForm;
