import React, { useMemo } from "react";
import { useNavigate } from "react-router-dom";
import MlApplicationParameterForm, { ML_APPLICATION_PARAMETER_FORM_FIELD_NAMES } from "components/MlApplicationParameterForm";
import MlApplicationsService from "services/MlApplicationsService";
import { ML_APPLICATIONS_PARAMETERS } from "urls";

const CreateMlApplicationParameterFormContainer = () => {
  const navigate = useNavigate();

  const { useCreateGlobalParameter } = MlApplicationsService();

  const { onCreate, isLoading } = useCreateGlobalParameter();

  const redirect = () => navigate(ML_APPLICATIONS_PARAMETERS);

  const onSubmit = (formData) => {
    onCreate(formData).then(() => {
      redirect();
    });
  };

  const onCancel = () => redirect();

  const defaultValues = useMemo(
    () => ({
      [ML_APPLICATION_PARAMETER_FORM_FIELD_NAMES.NAME]: "",
      [ML_APPLICATION_PARAMETER_FORM_FIELD_NAMES.KEY]: "",
      [ML_APPLICATION_PARAMETER_FORM_FIELD_NAMES.TENDENCY]: "",
      [ML_APPLICATION_PARAMETER_FORM_FIELD_NAMES.TARGET_VALUE]: 0,
      [ML_APPLICATION_PARAMETER_FORM_FIELD_NAMES.FUNCTION]: ""
    }),
    []
  );

  return (
    <MlApplicationParameterForm
      defaultValues={defaultValues}
      onSubmit={onSubmit}
      onCancel={onCancel}
      isSubmitLoading={isLoading}
    />
  );
};

export default CreateMlApplicationParameterFormContainer;
