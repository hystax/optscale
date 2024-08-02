import { useMemo } from "react";
import LeaderboardForm from "components/LeaderboardForm";
import { getDefaultValues } from "components/LeaderboardForm/utils";
import { useLeaderboardDatasetFormContainerData } from "hooks/useLeaderboardDatasetFormContainerData";
import MlLeaderboardsService from "services/MlLeaderboardsService";

const CreateLeaderboardDatasetFormContainer = ({ task, leaderboard, onSuccess, onCancel }) => {
  const {
    data: { datasets, datasetLabels, groupingTags },
    isLoading: isGetDataLoading
  } = useLeaderboardDatasetFormContainerData({
    taskId: task.id
  });

  const { useCreateLeaderboardDataset } = MlLeaderboardsService();
  const { isLoading: isCreateLeaderboardDatasetLoading, onCreate } = useCreateLeaderboardDataset();

  const defaultValues = useMemo(
    () =>
      getDefaultValues({
        name: "",
        selectedDatasets: [],
        tags: leaderboard.grouping_tags,
        groupByHyperparameters: leaderboard.group_by_hp,
        primaryMetric: leaderboard.primary_metric,
        secondaryMetrics: leaderboard.other_metrics,
        metricRestrictions: leaderboard.filters,
        datasetCoverageRules: leaderboard.dataset_coverage_rules
      }),
    [
      leaderboard.dataset_coverage_rules,
      leaderboard.filters,
      leaderboard.group_by_hp,
      leaderboard.grouping_tags,
      leaderboard.other_metrics,
      leaderboard.primary_metric
    ]
  );

  return (
    <LeaderboardForm
      defaultValues={defaultValues}
      onSubmit={(submitData) => onCreate(leaderboard.id, submitData).then(onSuccess)}
      onCancel={onCancel}
      datasets={datasets}
      groupingTags={groupingTags}
      metrics={task.metrics}
      datasetLabels={datasetLabels}
      isLoadingProps={{
        isGetDataLoading,
        isSubmitDataLoading: isCreateLeaderboardDatasetLoading
      }}
    />
  );
};

export default CreateLeaderboardDatasetFormContainer;
