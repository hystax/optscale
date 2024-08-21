import { useMemo } from "react";
import LeaderboardForm from "components/LeaderboardForm";
import { getDefaultValues } from "components/LeaderboardForm/utils";
import { useLeaderboardFormContainerData } from "hooks/useLeaderboardFormContainerData";
import MlLeaderboardsService from "services/MlLeaderboardsService";

const CloneLeaderboardFormContainer = ({ task, leaderboardTemplate, leaderboard, onSuccess, onCancel }) => {
  const {
    data: { datasets, datasetLabels, groupingTags },
    isLoading: isGetDataLoading
  } = useLeaderboardFormContainerData({
    taskId: task.id
  });

  const { useCreateLeaderboard } = MlLeaderboardsService();
  const { isLoading: isCreateLeaderboardLoading, onCreate } = useCreateLeaderboard();

  const defaultValues = useMemo(
    () =>
      getDefaultValues({
        name: `${leaderboard.name} - clone`,
        selectedDatasets: datasets.filter(({ id }) => leaderboard.dataset_ids.includes(id)),
        tags: leaderboard.grouping_tags,
        groupByHyperparameters: leaderboard.group_by_hp,
        primaryMetric: leaderboard.primary_metric,
        secondaryMetrics: leaderboard.other_metrics,
        metricRestrictions: leaderboard.filters,
        datasetCoverageRules: leaderboard.dataset_coverage_rules
      }),
    [
      datasets,
      leaderboard.dataset_coverage_rules,
      leaderboard.dataset_ids,
      leaderboard.filters,
      leaderboard.group_by_hp,
      leaderboard.grouping_tags,
      leaderboard.name,
      leaderboard.other_metrics,
      leaderboard.primary_metric
    ]
  );

  return (
    <LeaderboardForm
      defaultValues={defaultValues}
      onSubmit={(submitData) => onCreate(leaderboardTemplate.id, submitData).then(onSuccess)}
      onCancel={onCancel}
      datasets={datasets}
      groupingTags={groupingTags}
      metrics={task.metrics}
      datasetLabels={datasetLabels}
      isLoadingProps={{
        isGetDataLoading,
        isSubmitDataLoading: isCreateLeaderboardLoading
      }}
    />
  );
};

export default CloneLeaderboardFormContainer;
