import { useParams } from "react-router-dom";
import MlTaskDetails from "components/MlTaskDetails";
import MlTasksService from "services/MlTasksService";

const MlTaskDetailsContainer = () => {
  const { taskId } = useParams();

  const { useGetOne } = MlTasksService();

  const { task, isLoading, isDataReady } = useGetOne(taskId);

  return <MlTaskDetails isDataReady={isDataReady} isLoading={isLoading} task={task} />;
};

export default MlTaskDetailsContainer;
