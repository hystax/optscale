import { useNavigate, useParams } from "react-router-dom";
import MlEditTaskForm from "components/forms/MlEditTaskForm";
import EmployeesService from "services/EmployeesService";
import MlTasksService from "services/MlTasksService";
import { getMlTaskDetailsUrl } from "urls";
import { ML_TASK_DETAILS_TAB_NAME } from "utils/constants";
import { getQueryParams } from "utils/network";

const MlEditTaskFormContainer = ({ task }) => {
  const { taskId } = useParams();
  const navigate = useNavigate();

  const { useUpdateTask } = MlTasksService();
  const { onUpdate, isLoading } = useUpdateTask();

  const { useGet: useGetEmployees } = EmployeesService();
  const { isLoading: isGetEmployeesLoading, employees } = useGetEmployees();

  const redirectToTaskDetails = () => {
    const { [ML_TASK_DETAILS_TAB_NAME]: taskDetailsTab } = getQueryParams();

    return navigate(`${getMlTaskDetailsUrl(taskId)}?${ML_TASK_DETAILS_TAB_NAME}=${taskDetailsTab}`);
  };

  const onSubmit = (formData) => {
    onUpdate(taskId, formData).then(() => {
      redirectToTaskDetails();
    });
  };

  const onCancel = () => redirectToTaskDetails();

  return (
    <MlEditTaskForm
      task={task}
      onSubmit={onSubmit}
      onCancel={onCancel}
      employees={employees}
      isGetEmployeesLoading={isGetEmployeesLoading}
      isSubmitLoading={isLoading}
    />
  );
};

export default MlEditTaskFormContainer;
