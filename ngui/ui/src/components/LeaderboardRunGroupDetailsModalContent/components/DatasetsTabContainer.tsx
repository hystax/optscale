import MlModelsService from "services/MlModelsService";
import DatasetsTab from "./DatasetsTab";

const DatasetsTabContainer = ({ taskId, qualifiedRunIds, leaderboardDataset }) => {
  const { useGetModelRunsBulk } = MlModelsService();

  const { isLoading: isGetRunsBulkLoading, runs } = useGetModelRunsBulk(taskId, qualifiedRunIds);

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
