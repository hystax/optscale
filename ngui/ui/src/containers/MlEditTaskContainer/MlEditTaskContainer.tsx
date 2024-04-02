import { useParams } from "react-router-dom";
import MlEditTask from "components/MlEditTask";
import MlLeaderboardsService from "services/MlLeaderboardsService";
import MlTasksService from "services/MlTasksService";

const MlEditTaskContainer = () => {
  const { taskId } = useParams();

  const { useGetOne } = MlTasksService();
  const { task, isLoading: isGetTaskLoading } = useGetOne(taskId);

  const { useGetLeaderboard } = MlLeaderboardsService();
  const { isLoading: isGetLeaderboardLoading, leaderboard } = useGetLeaderboard(taskId);

  return <MlEditTask leaderboard={leaderboard} task={task} isLoading={isGetTaskLoading || isGetLeaderboardLoading} />;
};

export default MlEditTaskContainer;
