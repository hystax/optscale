import { useParams } from "react-router-dom";
import MlTaskRecommendations from "components/MlTaskRecommendations";
import MlTasksService from "services/MlTasksService";

const MlTaskRecommendationsContainer = () => {
  const { taskId } = useParams();

  const { useGetTaskRecommendations } = MlTasksService();
  const { isLoading: isGetRecommendationsLoading, recommendations } = useGetTaskRecommendations(taskId);

  return <MlTaskRecommendations taskId={taskId} isLoading={isGetRecommendationsLoading} recommendations={recommendations} />;
};

export default MlTaskRecommendationsContainer;
