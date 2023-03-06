import React from "react";
import { useNavigate } from "react-router-dom";
import MlModelCreateForm from "components/MlModelCreateForm";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import EmployeesService from "services/EmployeesService";
import MlApplicationsService from "services/MlApplicationsService";
import { ML_APPLICATIONS } from "urls";
import { getParameters } from "utils/mlDemoData/parameters";

const DemoContainer = ({ employees, isGetEmployeesLoading }) => {
  const navigate = useNavigate();

  const redirect = () => navigate(ML_APPLICATIONS);

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
        isCreateApplicationLoading: false,
        isGetGlobalParametersLoading: false
      }}
    />
  );
};

const Container = ({ employees, isGetEmployeesLoading }) => {
  const navigate = useNavigate();

  const { useCreateApplication, useGetGlobalParameters } = MlApplicationsService();
  const { isLoading: isGetGlobalParametersLoading, parameters: globalParameters } = useGetGlobalParameters();

  const { isLoading: isCreateApplicationLoading, onCreate } = useCreateApplication();

  const redirect = () => navigate(ML_APPLICATIONS);

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
        isCreateApplicationLoading,
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
