import MlTasks from "components/MlTasks";
import MlTasksService from "services/MlTasksService";

const MlTasksContainer = () => {
  const { useGetAll } = MlTasksService();

  const { isLoading, tasks } = useGetAll();

  return <MlTasks tasks={tasks} isLoading={isLoading} />;
};

export default MlTasksContainer;
