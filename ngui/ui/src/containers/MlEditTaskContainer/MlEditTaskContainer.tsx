import { useParams } from "react-router-dom";
import MlEditTask from "components/MlEditTask";
import MlLeaderboardsService from "services/MlLeaderboardsService";
import MlTasksService from "services/MlTasksService";

const MlEditTaskContainer = () => {
  const { taskId } = useParams() as { taskId: string };

  const { useGetOne } = MlTasksService();
  const { task, isLoading: isGetTaskLoading } = useGetOne(taskId);

  const { useGetLeaderboardTemplate } = MlLeaderboardsService();
  const { isLoading: isGetLeaderboardTemplateLoading, leaderboardTemplate } = useGetLeaderboardTemplate(taskId);

  return (
    <MlEditTask
      task={task}
      leaderboardTemplate={leaderboardTemplate}
      isLoading={isGetTaskLoading || isGetLeaderboardTemplateLoading}
    />
  );
};

export default MlEditTaskContainer;
