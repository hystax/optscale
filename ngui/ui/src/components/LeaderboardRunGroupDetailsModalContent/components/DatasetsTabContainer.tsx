import MlTasksService from "services/MlTasksService";
import DatasetsTab from "./DatasetsTab";

const DatasetsTabContainer = ({ taskId, qualifiedRunIds, leaderboardDataset }) => {
  const { useGetTaskRunsBulk } = MlTasksService();

  const { isLoading: isGetRunsBulkLoading, runs } = useGetTaskRunsBulk(taskId, qualifiedRunIds);

  return (
    <DatasetsTab
      isLoading={isGetRunsBulkLoading}
      datasets={leaderboardDataset.datasets.map((datum) => ({
        ...datum,
        covered_by: runs.find(({ dataset: { id: datasetId } = {} }) => datasetId === datum.id)
      }))}
    />
  );
};

export default DatasetsTabContainer;
