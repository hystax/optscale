import MlDatasetsService from "services/MlDatasetsService";
import MlTasksService from "services/MlTasksService";

type UseLeaderboardDatasetFormContainerDataParams = {
  taskId: string;
};

export const useLeaderboardDatasetFormContainerData = ({ taskId }: UseLeaderboardDatasetFormContainerDataParams) => {
  const { useGetAll, useGetLabels } = MlDatasetsService();
  const { isLoading: isDatasetsLoading, datasets } = useGetAll();
  const { isLoading: isDatasetLabelsLoading, labels: datasetLabels } = useGetLabels();

  const { useGetTaskTags } = MlTasksService();
  const { isLoading: isGetTaskTagsLoading, tags } = useGetTaskTags(taskId);

  return {
    data: {
      datasets,
      datasetLabels,
      groupingTags: tags
    },
    isLoading: isDatasetsLoading || isDatasetLabelsLoading || isGetTaskTagsLoading
  };
};
