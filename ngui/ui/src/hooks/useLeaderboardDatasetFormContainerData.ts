import { useMemo } from "react";
import MlDatasetsService from "services/MlDatasetsService";
import MlTasksService from "services/MlTasksService";

type UseLeaderboardDatasetFormContainerDataParams = {
  taskId: string;
};

export const useLeaderboardDatasetFormContainerData = ({ taskId }: UseLeaderboardDatasetFormContainerDataParams) => {
  const { useGetAll, useGetLabels } = MlDatasetsService();
  const { isLoading: isDatasetsLoading, datasets } = useGetAll();
  const { isLoading: isDatasetLabelsLoading, labels: datasetLabels } = useGetLabels();

  const { useGetTaskRunsList } = MlTasksService();
  const { isLoading: isGetRunsListLoading, runs } = useGetTaskRunsList(taskId);

  const runTags = useMemo(() => Array.from(new Set(runs.flatMap((run) => Object.keys(run.tags)))), [runs]);

  return {
    data: {
      datasets,
      datasetLabels,
      runTags
    },
    isLoading: isDatasetsLoading || isDatasetLabelsLoading || isGetRunsListLoading
  };
};
