import { useParams } from "react-router-dom";
import MlTaskRunsList from "components/MlTaskRunsList";
import MlTasksService from "services/MlTasksService";

const MlTaskRunsListContainer = () => {
  const { taskId } = useParams();

  const { useGetTaskRunsList } = MlTasksService();
  const { runs = [], isLoading, isDataReady } = useGetTaskRunsList(taskId);

  return <MlTaskRunsList runs={runs} isLoading={isLoading || !isDataReady} />;
};

export default MlTaskRunsListContainer;
