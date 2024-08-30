import { useMemo } from "react";
import LeaderboardForm from "components/LeaderboardForm";
import { getDefaultValues } from "components/LeaderboardForm/utils";
import { useLeaderboardFormContainerData } from "hooks/useLeaderboardFormContainerData";
import MlLeaderboardsService from "services/MlLeaderboardsService";

const CreateLeaderboardFormContainer = ({ task, leaderboardTemplate, onSuccess, onCancel }) => {
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
        name: "",
        selectedDatasets: [],
        tags: leaderboardTemplate.grouping_tags,
        groupByHyperparameters: leaderboardTemplate.group_by_hp,
        primaryMetric: leaderboardTemplate.primary_metric,
        secondaryMetrics: leaderboardTemplate.other_metrics,
        metricRestrictions: leaderboardTemplate.filters,
        datasetCoverageRules: leaderboardTemplate.dataset_coverage_rules
      }),
    [
      leaderboardTemplate.dataset_coverage_rules,
      leaderboardTemplate.filters,
      leaderboardTemplate.group_by_hp,
      leaderboardTemplate.grouping_tags,
      leaderboardTemplate.other_metrics,
      leaderboardTemplate.primary_metric
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

export default CreateLeaderboardFormContainer;
