import { useMemo } from "react";
import LeaderboardForm from "components/LeaderboardForm";
import { getDefaultValues } from "components/LeaderboardForm/utils";
import { useLeaderboardFormContainerData } from "hooks/useLeaderboardFormContainerData";
import MlLeaderboardsService from "services/MlLeaderboardsService";

const EditLeaderboardFormContainer = ({ task, leaderboard, onSuccess, onCancel }) => {
  const {
    data: { datasets, datasetLabels, groupingTags },
    isLoading: isGetDataLoading
  } = useLeaderboardFormContainerData({
    taskId: task.id
  });

  const { useUpdateLeaderboard } = MlLeaderboardsService();
  const { isLoading: isUpdateLeaderboardLoading, onUpdate } = useUpdateLeaderboard();

  const defaultValues = useMemo(
    () =>
      getDefaultValues({
        name: leaderboard.name,
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
      onSubmit={(submitData) => onUpdate(leaderboard.id, submitData).then(onSuccess)}
      onCancel={onCancel}
      datasets={datasets}
      groupingTags={groupingTags}
      metrics={task.metrics}
      datasetLabels={datasetLabels}
      isLoadingProps={{
        isGetDataLoading,
        isSubmitDataLoading: isUpdateLeaderboardLoading
      }}
    />
  );
};

export default EditLeaderboardFormContainer;
