import { useNavigate } from "react-router-dom";
import MlModelCreateForm from "components/MlModelCreateForm";
import EmployeesService from "services/EmployeesService";
import MlModelsService from "services/MlModelsService";
import { ML_TASKS } from "urls";

const MlModelCreateFormContainer = () => {
  const { useGet: useGetEmployees } = EmployeesService();
  const { isLoading: isGetEmployeesLoading, employees } = useGetEmployees();

  const navigate = useNavigate();

  const { useCreateModel, useGetGlobalParameters } = MlModelsService();
  const { isLoading: isGetGlobalParametersLoading, parameters: globalParameters } = useGetGlobalParameters();

  const { isLoading: isCreateModelLoading, onCreate } = useCreateModel();

  const redirect = () => navigate(ML_TASKS);

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

export default MlModelCreateFormContainer;
