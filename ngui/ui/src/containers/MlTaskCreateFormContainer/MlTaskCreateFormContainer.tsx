import { useNavigate } from "react-router-dom";
import MlTaskCreateForm from "components/MlTaskCreateForm";
import EmployeesService from "services/EmployeesService";
import MlTasksService from "services/MlTasksService";
import { ML_TASKS } from "urls";

const MlTaskCreateFormContainer = () => {
  const { useGet: useGetEmployees } = EmployeesService();
  const { isLoading: isGetEmployeesLoading, employees } = useGetEmployees();

  const navigate = useNavigate();

  const { useCreateTask, useGetGlobalMetrics } = MlTasksService();
  const { isLoading: isGetGlobalMetricsLoading, metrics: globalMetrics } = useGetGlobalMetrics();

  const { isLoading: isCreateTaskLoading, onCreate } = useCreateTask();

  const redirect = () => navigate(ML_TASKS);

  const onSubmit = (formData) => {
    onCreate(formData).then(() => redirect());
  };

  const onCancel = () => redirect();

  return (
    <MlTaskCreateForm
      onSubmit={onSubmit}
      onCancel={onCancel}
      metrics={globalMetrics}
      employees={employees}
      isLoading={{
        isGetEmployeesLoading,
        isCreateTaskLoading,
        isGetGlobalMetricsLoading
      }}
    />
  );
};

export default MlTaskCreateFormContainer;
