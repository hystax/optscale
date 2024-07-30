import { useNavigate, useParams } from "react-router-dom";
import SetupLeaderboard from "components/SetupLeaderboard";
import MlDatasetsService from "services/MlDatasetsService";
import MlLeaderboardsService from "services/MlLeaderboardsService";
import MlTasksService from "services/MlTasksService";
import { getMlTaskDetailsUrl } from "urls";

const SetupLeaderboardContainer = () => {
  const { taskId } = useParams();
  const navigate = useNavigate();

  const mlTaskDetailsUrl = getMlTaskDetailsUrl(taskId);

  const { useGetOne, useGetTaskRunsList } = MlTasksService();

  const { useGetLabels: useGetDatasetLabels } = MlDatasetsService();
  const { isLoading: isGetDatasetLabelsLoading, labels: datasetLabels } = useGetDatasetLabels();

  const { isLoading: isGetTaskLoading, task } = useGetOne(taskId);
  const { isLoading: isGetRunsListLoading, runs } = useGetTaskRunsList(taskId);

  const { useCreateLeaderboard } = MlLeaderboardsService();
  const { isLoading: isCreateLeaderboardLoading, onCreate } = useCreateLeaderboard();

  return (
    <SetupLeaderboard
      onSetup={(formData) => {
        onCreate(taskId, formData).then(() => navigate(mlTaskDetailsUrl));
      }}
      task={task}
      runs={runs}
      datasetLabels={datasetLabels}
      isLoadingProps={{
        isGetTaskLoading,
        isGetRunsListLoading,
        isGetDatasetLabelsLoading,
        isSetupLoading: isCreateLeaderboardLoading
      }}
    />
  );
};

export default SetupLeaderboardContainer;
