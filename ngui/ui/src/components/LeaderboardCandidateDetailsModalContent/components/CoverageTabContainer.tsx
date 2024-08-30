import MlDatasetsService from "services/MlDatasetsService";
import MlTasksService from "services/MlTasksService";
import CoverageTab from "./CoverageTab";

const CoverageTabContainer = ({ taskId, qualifiedRunIds, leaderboard, candidateDetails }) => {
  const { useGetTaskRunsBulk } = MlTasksService();
  const { isLoading: isGetRunsBulkLoading, runs } = useGetTaskRunsBulk(taskId, qualifiedRunIds);

  const { useGetAll } = MlDatasetsService();
  const { isLoading: isDatasetsLoading, datasets } = useGetAll();

  return (
    <CoverageTab
      datasetCoverage={Object.fromEntries(
        candidateDetails?.coverage?.coverageRules
          .map(({ label }) => [label, candidateDetails.dataset_coverage[label] ?? []])
          .map(([label, datasetIds]) => [
            label,
            datasetIds
              .map((datasetId) => {
                const dataset = datasets.find(({ id }) => id === datasetId);

                if (!dataset) {
                  return null;
                }

                return {
                  ...dataset,
                  covered_by: runs.find((run) => run.dataset?.id === datasetId)
                };
              })
              .filter(Boolean)
          ]) ?? []
      )}
      datasets={leaderboard.datasets.map((datum) => ({
        ...datum,
        covered_by: runs.find(({ dataset: { id: datasetId } = {} }) => datasetId === datum.id)
      }))}
      isLoading={isGetRunsBulkLoading || isDatasetsLoading}
    />
  );
};

export default CoverageTabContainer;
