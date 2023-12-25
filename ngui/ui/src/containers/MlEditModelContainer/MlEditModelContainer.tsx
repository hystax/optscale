import { useParams } from "react-router-dom";
import MlEditModel from "components/MlEditModel";
import MlLeaderboardsService from "services/MlLeaderboardsService";
import MlModelsService from "services/MlModelsService";

const MlEditModelContainer = () => {
  const { taskId } = useParams();

  const { useGetOne } = MlModelsService();
  const { model, isLoading: isGetTaskLoading } = useGetOne(taskId);

  const { useGetLeaderboard } = MlLeaderboardsService();
  const { isLoading: isGetLeaderboardLoading, leaderboard } = useGetLeaderboard(taskId);

  return <MlEditModel leaderboard={leaderboard} model={model} isLoading={isGetTaskLoading || isGetLeaderboardLoading} />;
};

export default MlEditModelContainer;
