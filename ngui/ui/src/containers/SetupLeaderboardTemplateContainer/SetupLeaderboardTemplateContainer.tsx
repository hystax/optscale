import { useNavigate, useParams } from "react-router-dom";
import SetupLeaderboardTemplate from "components/SetupLeaderboardTemplate";
import MlDatasetsService from "services/MlDatasetsService";
import MlLeaderboardsService from "services/MlLeaderboardsService";
import MlTasksService from "services/MlTasksService";
import { getMlTaskDetailsUrl } from "urls";

const SetupLeaderboardTemplateContainer = () => {
  const { taskId } = useParams();
  const navigate = useNavigate();

  const mlTaskDetailsUrl = getMlTaskDetailsUrl(taskId);

  const { useGetOne, useGetTaskTags } = MlTasksService();
  const { isLoading: isGetTaskLoading, task } = useGetOne(taskId);
  const { isLoading: isGetTaskTagsLoading, tags } = useGetTaskTags(taskId);

  const { useGetLabels: useGetDatasetLabels } = MlDatasetsService();
  const { isLoading: isGetDatasetLabelsLoading, labels: datasetLabels } = useGetDatasetLabels();

  const { useCreateLeaderboardTemplate } = MlLeaderboardsService();
  const { isLoading: isCreateLeaderboardLoading, onCreate } = useCreateLeaderboardTemplate();

  return (
    <SetupLeaderboardTemplate
      onSetup={(formData) => {
        onCreate(taskId, formData).then(() => navigate(mlTaskDetailsUrl));
      }}
      task={task}
      groupingTags={tags}
      datasetLabels={datasetLabels}
      isLoadingProps={{
        isGetTaskLoading,
        isGetTaskTagsLoading,
        isGetDatasetLabelsLoading,
        isSetupLoading: isCreateLeaderboardLoading
      }}
    />
  );
};

export default SetupLeaderboardTemplateContainer;
