import { useMemo } from "react";
import LeaderboardForm from "components/LeaderboardForm";
import { getDefaultValues } from "components/LeaderboardForm/utils";
import { useLeaderboardDatasetFormContainerData } from "hooks/useLeaderboardDatasetFormContainerData";
import MlLeaderboardsService from "services/MlLeaderboardsService";

const CloneLeaderboardDatasetFormContainer = ({ task, leaderboard, leaderboardDataset, onSuccess, onCancel }) => {
  const {
    data: { datasets, datasetLabels, runTags },
    isLoading: isGetDataLoading
  } = useLeaderboardDatasetFormContainerData({
    taskId: task.id
  });

  const { useCreateLeaderboardDataset } = MlLeaderboardsService();
  const { isLoading: isCreateLeaderboardDatasetLoading, onCreate } = useCreateLeaderboardDataset();

  const defaultValues = useMemo(
    () =>
      getDefaultValues({
        name: `${leaderboardDataset.name} - clone`,
        selectedDatasets: datasets.filter(({ id }) => leaderboardDataset.dataset_ids.includes(id)),
        tags: leaderboardDataset.grouping_tags,
        groupByHyperparameters: leaderboardDataset.group_by_hp,
        primaryMetric: leaderboardDataset.primary_metric,
        secondaryMetrics: leaderboardDataset.other_metrics,
        metricRestrictions: leaderboardDataset.filters,
        datasetCoverageRules: leaderboardDataset.dataset_coverage_rules
      }),
    [
      datasets,
      leaderboardDataset.dataset_coverage_rules,
      leaderboardDataset.dataset_ids,
      leaderboardDataset.filters,
      leaderboardDataset.group_by_hp,
      leaderboardDataset.grouping_tags,
      leaderboardDataset.name,
      leaderboardDataset.other_metrics,
      leaderboardDataset.primary_metric
    ]
  );

  return (
    <LeaderboardForm
      defaultValues={defaultValues}
      onSubmit={(submitData) => onCreate(leaderboard.id, submitData).then(onSuccess)}
      onCancel={onCancel}
      datasets={datasets}
      runTags={runTags}
      metrics={task.metrics}
      datasetLabels={datasetLabels}
      isLoadingProps={{
        isGetDataLoading,
        isSubmitDataLoading: isCreateLeaderboardDatasetLoading
      }}
    />
  );
};

export default CloneLeaderboardDatasetFormContainer;
