import React, { useMemo } from "react";
import { useNavigate } from "react-router-dom";
import MlModelParameterForm, { ML_MODEL_PARAMETER_FORM_FIELD_NAMES } from "components/MlModelParameterForm";
import MlModelsService from "services/MlModelsService";
import { ML_MODELS_PARAMETERS } from "urls";

const CreateMlModelParameterFormContainer = () => {
  const navigate = useNavigate();

  const { useCreateGlobalParameter } = MlModelsService();

  const { onCreate, isLoading } = useCreateGlobalParameter();

  const redirect = () => navigate(ML_MODELS_PARAMETERS);

  const onSubmit = (formData) => {
    onCreate(formData).then(() => {
      redirect();
    });
  };

  const onCancel = () => redirect();

  const defaultValues = useMemo(
    () => ({
      [ML_MODEL_PARAMETER_FORM_FIELD_NAMES.NAME]: "",
      [ML_MODEL_PARAMETER_FORM_FIELD_NAMES.KEY]: "",
      [ML_MODEL_PARAMETER_FORM_FIELD_NAMES.TENDENCY]: "",
      [ML_MODEL_PARAMETER_FORM_FIELD_NAMES.TARGET_VALUE]: 0,
      [ML_MODEL_PARAMETER_FORM_FIELD_NAMES.FUNCTION]: ""
    }),
    []
  );

  return (
    <MlModelParameterForm defaultValues={defaultValues} onSubmit={onSubmit} onCancel={onCancel} isSubmitLoading={isLoading} />
  );
};

export default CreateMlModelParameterFormContainer;
