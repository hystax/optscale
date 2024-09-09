import { useNavigate } from "react-router-dom";
import MlTaskCreateForm from "components/forms/MlTaskCreateForm";
import EmployeesService from "services/EmployeesService";
import MlMetricsService from "services/MlMetricsService";
import MlTasksService from "services/MlTasksService";
import { ML_TASKS } from "urls";

const MlTaskCreateFormContainer = () => {
  const { useGet: useGetEmployees } = EmployeesService();
  const { isLoading: isGetEmployeesLoading, employees } = useGetEmployees();

  const navigate = useNavigate();

  const { useCreateTask } = MlTasksService();
  const { useGetMlMetrics } = MlMetricsService();
  const { isLoading: isGetMlMetricsLoading, metrics: globalMetrics } = useGetMlMetrics();

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
        isGetMlMetricsLoading
      }}
    />
  );
};

export default MlTaskCreateFormContainer;
