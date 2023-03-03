import React, { useMemo } from "react";
import { useNavigate, useParams } from "react-router-dom";
import MlApplicationParameterForm, { ML_APPLICATION_PARAMETER_FORM_FIELD_NAMES } from "components/MlApplicationParameterForm";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import MlApplicationsService from "services/MlApplicationsService";
import { ML_APPLICATIONS_PARAMETERS } from "urls";
import { getParameter } from "utils/mlDemoData/parameters";

const DemoContainer = () => {
  const navigate = useNavigate();

  const { parameterId } = useParams();

  const parameter = useMemo(() => getParameter(parameterId), [parameterId]);

  const redirect = () => navigate(ML_APPLICATIONS_PARAMETERS);

  const onSubmit = () => {};

  const onCancel = () => redirect();

  const defaultValues = useMemo(
    () => ({
      [ML_APPLICATION_PARAMETER_FORM_FIELD_NAMES.NAME]: parameter.name ?? "",
      [ML_APPLICATION_PARAMETER_FORM_FIELD_NAMES.TENDENCY]: parameter.tendency ?? "",
      [ML_APPLICATION_PARAMETER_FORM_FIELD_NAMES.TARGET_VALUE]: parameter.target_value ?? "",
      [ML_APPLICATION_PARAMETER_FORM_FIELD_NAMES.FUNCTION]: parameter.func ?? ""
    }),
    [parameter.name, parameter.func, parameter.target_value, parameter.tendency]
  );

  return (
    <MlApplicationParameterForm
      defaultValues={defaultValues}
      onSubmit={onSubmit}
      onCancel={onCancel}
      isGetLoading={false}
      isSubmitLoading={false}
      isEdit
    />
  );
};

const Container = () => {
  const navigate = useNavigate();

  const { parameterId } = useParams();

  const { useAlwaysGetGlobalParameter, useUpdateGlobalParameter } = MlApplicationsService();

  const { isLoading: isGetGlobalParameterLoading, parameter } = useAlwaysGetGlobalParameter(parameterId);

  const { onUpdate, isLoading: isUpdateGlobalParameterLoading } = useUpdateGlobalParameter(parameterId);

  const redirect = () => navigate(ML_APPLICATIONS_PARAMETERS);

  const onSubmit = (formData) => {
    onUpdate(formData).then(() => {
      redirect();
    });
  };

  const onCancel = () => redirect();

  const defaultValues = useMemo(
    () => ({
      [ML_APPLICATION_PARAMETER_FORM_FIELD_NAMES.NAME]: parameter.name ?? "",
      [ML_APPLICATION_PARAMETER_FORM_FIELD_NAMES.TENDENCY]: parameter.tendency ?? "",
      [ML_APPLICATION_PARAMETER_FORM_FIELD_NAMES.TARGET_VALUE]: parameter.target_value ?? "",
      [ML_APPLICATION_PARAMETER_FORM_FIELD_NAMES.FUNCTION]: parameter.func ?? ""
    }),
    [parameter.name, parameter.func, parameter.target_value, parameter.tendency]
  );

  return (
    <MlApplicationParameterForm
      defaultValues={defaultValues}
      onSubmit={onSubmit}
      onCancel={onCancel}
      isGetLoading={isGetGlobalParameterLoading}
      isSubmitLoading={isUpdateGlobalParameterLoading}
      isEdit
    />
  );
};

const EditMlApplicationParameterFormContainer = () => {
  const { isDemo } = useOrganizationInfo();

  return isDemo ? <DemoContainer /> : <Container />;
};

export default EditMlApplicationParameterFormContainer;
