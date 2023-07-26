import React from "react";
import { useNavigate } from "react-router-dom";
import MlModelCreateForm from "components/MlModelCreateForm";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import EmployeesService from "services/EmployeesService";
import MlModelsService from "services/MlModelsService";
import { ML_MODELS } from "urls";
import { getParameters } from "utils/mlDemoData/parameters";

const DemoContainer = ({ employees, isGetEmployeesLoading }) => {
  const navigate = useNavigate();

  const redirect = () => navigate(ML_MODELS);

  const onSubmit = () => {};

  const onCancel = () => redirect();

  return (
    <MlModelCreateForm
      onSubmit={onSubmit}
      onCancel={onCancel}
      parameters={getParameters()}
      employees={employees}
      isLoading={{
        isGetEmployeesLoading,
        isCreateModelLoading: false,
        isGetGlobalParametersLoading: false
      }}
    />
  );
};

const Container = ({ employees, isGetEmployeesLoading }) => {
  const navigate = useNavigate();

  const { useCreateModel, useGetGlobalParameters } = MlModelsService();
  const { isLoading: isGetGlobalParametersLoading, parameters: globalParameters } = useGetGlobalParameters();

  const { isLoading: isCreateModelLoading, onCreate } = useCreateModel();

  const redirect = () => navigate(ML_MODELS);

  const onSubmit = (formData) => {
    onCreate(formData).then(() => redirect());
  };

  const onCancel = () => redirect();

  return (
    <MlModelCreateForm
      onSubmit={onSubmit}
      onCancel={onCancel}
      parameters={globalParameters}
      employees={employees}
      isLoading={{
        isGetEmployeesLoading,
        isCreateModelLoading,
        isGetGlobalParametersLoading
      }}
    />
  );
};

const MlModelCreateFormContainer = () => {
  const { isDemo } = useOrganizationInfo();

  const { useGet: useGetEmployees } = EmployeesService();
  const { isLoading: isGetEmployeesLoading, employees } = useGetEmployees();

  return isDemo ? (
    <DemoContainer employees={employees} isGetEmployeesLoading={isGetEmployeesLoading} />
  ) : (
    <Container employees={employees} isGetEmployeesLoading={isGetEmployeesLoading} />
  );
};

export default MlModelCreateFormContainer;
