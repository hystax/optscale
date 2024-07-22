import MlArtifacts from "components/MlArtifacts";
import MlTasksService from "services/MlTasksService";

const MlArtifactsPageContainer = () => {
  const { useGetAll: useGetAllTasks } = MlTasksService();
  const { tasks, isLoading } = useGetAllTasks();

  return <MlArtifacts tasks={tasks} isLoading={isLoading} />;
};

export default MlArtifactsPageContainer;
