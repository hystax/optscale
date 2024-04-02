import { useParams } from "react-router-dom";
import TaskSummaryGrid from "components/MlTaskDetails/TaskSummaryGrid";
import MlTasksService from "services/MlTasksService";

const MlTaskSummaryCardsContainer = ({ task, isTaskDetailsLoading }) => {
  const { taskId } = useParams();

  const { useGetTaskRecommendations } = MlTasksService();
  const { isLoading: isGetRecommendationsLoading, recommendations } = useGetTaskRecommendations(taskId);

  return (
    <TaskSummaryGrid
      task={task}
      recommendations={recommendations}
      isTaskDetailsLoading={isTaskDetailsLoading}
      isGetRecommendationsLoading={isGetRecommendationsLoading}
    />
  );
};

export default MlTaskSummaryCardsContainer;
